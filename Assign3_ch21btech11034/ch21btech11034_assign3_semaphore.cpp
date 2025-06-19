#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <chrono>
#include <thread>
#include <random>
#include <semaphore.h>
#include <pthread.h>
#include <cstdlib>
#include <algorithm>

using namespace std;
using namespace std::chrono;

int capacity, np, nc, cntp, cntc;
double mu_p, mu_c; 
vector<int> buffer;
int in_index = 0, out_index = 0;

sem_t sem_empty; 
sem_t sem_full;  
sem_t sem_mutex; 


vector<string> logBuffers;

steady_clock::time_point base_time;


void writeOutputToFile(const string &output)
{
    ofstream outFile("output_sems.txt", ios::app);
    if (outFile)
        outFile << output << endl;
    else
        cout << "Error: Could not open output file." << endl;
    outFile.close();
}

vector<string> splitByNewline(const string &buffer)
{
    vector<string> lines;
    size_t start = 0, end;
    while ((end = buffer.find('\n', start)) != string::npos)
    {
        string line = buffer.substr(start, end - start);
        if (!line.empty())
            lines.push_back(line);
        start = end + 1;
    }
    if (start < buffer.size())
        lines.push_back(buffer.substr(start));
    return lines;
}

void parseAndWriteLogs(const vector<string> &buffers)
{
    vector<pair<long long, string>> logs;
    for (const string &buffer : buffers)
    {
        vector<string> lines = splitByNewline(buffer);
        for (const string &line : lines)
        {
            size_t lastSpace = line.find_last_of(' ');
            if (lastSpace != string::npos)
            {
                string logMessage = line.substr(0, lastSpace);
                string lastToken = line.substr(lastSpace + 1);
                try
                {
                    long long timestamp = stoll(lastToken);
                    logs.emplace_back(timestamp, logMessage);
                }
                catch (const std::invalid_argument &e)
                {
                    // Skip lines where the last token is not a number (e.g., total execution time line)
                    continue;
                }
            }
        }
    }
    sort(logs.begin(), logs.end(), [](const pair<long long, string> &a, const pair<long long, string> &b)
         { return a.first < b.first; });
    // Clear the output file first
    ofstream clearFile("output_sems.txt", ios::out);
    clearFile.close();
    for (const auto &log : logs)
    {
        writeOutputToFile(log.second + " " + to_string(log.first));
    }
}

long long getTimestamp()
{
    auto now = steady_clock::now();
    return duration_cast<nanoseconds>(now - base_time).count();
}

// Producer thread function
void *producer(void *arg)
{
    int global_id = *(int *)arg; 
    // Set up a random generator for exponential delay (mean = mu_p ms)
    default_random_engine generator(random_device{}());
    exponential_distribution<double> exp_dist(1.0 / mu_p); // mean delay in ms

    for (int i = 0; i < cntp; i++)
    {
        int item = global_id * 1000 + i; 

        sem_wait(&sem_empty);
        long long cs_entry = getTimestamp();
        sem_wait(&sem_mutex);
        int pos = in_index;
        buffer[in_index] = item;
        in_index = (in_index + 1) % capacity;
        long long cs_exit = getTimestamp();
        {
            ostringstream oss;
            oss << "PROD_CS: " << global_id << " " << cs_entry << " " << cs_exit;
            logBuffers[global_id] += oss.str() + "\n";
        }
        {
            ostringstream oss;
            oss << (i + 1) << "th item produced by thread " << global_id
                << " at " << cs_exit << " ms into buffer location " << pos;
            logBuffers[global_id] += oss.str() + "\n";
        }

        sem_post(&sem_mutex);
        sem_post(&sem_full);

        // Sleep for an exponentially distributed delay
        double delay_ms = exp_dist(generator);
        this_thread::sleep_for(milliseconds(static_cast<int>(delay_ms)));
    }
    pthread_exit(NULL);
    return NULL;
}

// Consumer thread function
void *consumer(void *arg)
{
    int global_id = *(int *)arg; 
    // Set up a random generator for exponential delay (mean = mu_c ms)
    default_random_engine generator(random_device{}());
    exponential_distribution<double> exp_dist(1.0 / mu_c);

    for (int i = 0; i < cntc; i++)
    {
        sem_wait(&sem_full);
        long long cs_entry = getTimestamp();
        sem_wait(&sem_mutex);

        int pos = out_index;
        int item = buffer[out_index];
        out_index = (out_index + 1) % capacity;

        long long cs_exit = getTimestamp();
        {
            ostringstream oss;
            oss << "CONS_CS: " << global_id << " " << cs_entry << " " << cs_exit;
            logBuffers[global_id] += oss.str() + "\n";
        }
        {
            ostringstream oss;
            oss << (i + 1) << "th item consumed by thread " << global_id
                << " at " << cs_exit << " ms from buffer location " << pos;
            logBuffers[global_id] += oss.str() + "\n";
        }

        sem_post(&sem_mutex);
        sem_post(&sem_empty);

        // Sleep for an exponentially distributed delay
        double delay_ms = exp_dist(generator);
        this_thread::sleep_for(milliseconds(static_cast<int>(delay_ms)));
    }
    pthread_exit(NULL);
    return NULL;
}


int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        cerr << "Usage: " << argv[0] << " inp-params.txt" << endl;
        return 1;
    }

    ifstream inputFile(argv[1]);
    if (!inputFile)
    {
        cerr << "Error: Cannot open input file " << argv[1] << endl;
        return 1;
    }
    inputFile >> capacity >> np >> nc >> cntp >> cntc >> mu_p >> mu_c;
    inputFile.close();

    buffer.resize(capacity, 0);

    sem_init(&sem_empty, 0, capacity);
    sem_init(&sem_full, 0, 0);
    sem_init(&sem_mutex, 0, 1);

    int totalThreads = np + nc;
    logBuffers.resize(totalThreads, "");

    base_time = steady_clock::now();

    vector<pthread_t> producerThreads(np);
    vector<pthread_t> consumerThreads(nc);
    vector<int> producer_global_ids(np), consumer_global_ids(nc);

    for (int i = 0; i < np; i++)
    {
        producer_global_ids[i] = i;
        if (pthread_create(&producerThreads[i], NULL, producer, &producer_global_ids[i]) != 0)
        {
            cerr << "Error: Unable to create producer thread " << i << endl;
            return 1;
        }
    }

    for (int i = 0; i < nc; i++)
    {
        consumer_global_ids[i] = i + np;
        if (pthread_create(&consumerThreads[i], NULL, consumer, &consumer_global_ids[i]) != 0)
        {
            cerr << "Error: Unable to create consumer thread " << i << endl;
            return 1;
        }
    }

    for (int i = 0; i < np; i++)
    {
        pthread_join(producerThreads[i], NULL);
    }
    for (int i = 0; i < nc; i++)
    {
        pthread_join(consumerThreads[i], NULL);
    }

    long long totalDuration = duration_cast<milliseconds>(steady_clock::now() - base_time).count();
    ostringstream oss;
    oss << "Total execution time: " << totalDuration << " ms";
    logBuffers[0] += oss.str() + "\n";

    parseAndWriteLogs(logBuffers);

    sem_destroy(&sem_empty);
    sem_destroy(&sem_full);
    sem_destroy(&sem_mutex);

    return 0;
}
