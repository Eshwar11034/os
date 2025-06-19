#include <iostream>
#include <bits/stdc++.h>
#include <pthread.h>
#include <chrono>

using namespace std;

int N, K;
vector<vector<int>> sudoku;
vector<string> Buffers;
string output_filename = "output.txt";
bool use_cyclic = false;
bool use_sequential = false;
class thread_data
{
public:
    int thread_id;
    int nrows;
    int ncols;
    int nsubs;
    int start_row;
    int start_col;
    int start_sub;
    bool terminate;
};

long long base_timestamp;

int subCheck(int s)
{
    int sq_root = sqrt(N);
    if (sq_root * sq_root != N)
    {
        cout << "Error: N must be a perfect square." << endl;
        return -1;
    }
    vector<int> sub(N, 0);
    int r = (s / sq_root) * sq_root;
    int c = (s % sq_root) * sq_root;
    for (int i = r; i < r + sq_root; i++)
    {
        for (int j = c; j < c + sq_root; j++)
        {
            if (sudoku[i][j] < 1 || sudoku[i][j] > N || sub[sudoku[i][j] - 1] == 1)
                return -1;

            else
                sub[sudoku[i][j] - 1] = 1;
        }
    }
    return s;
}

int rowCheck(int r)
{
    vector<int> row(N, 0);
    for (int j = 0; j < N; j++)
    {
        if (sudoku[r][j] < 1 || sudoku[r][j] > N || row[sudoku[r][j] - 1] == 1)
            return -1;

        else
            row[sudoku[r][j] - 1] = 1;
    }
    return r;
}

int colCheck(int c)
{
    vector<int> col(N, 0);
    for (int j = 0; j < N; j++)
    {
        if (sudoku[j][c] < 1 || sudoku[j][c] > N || col[sudoku[j][c] - 1] == 1)
            return -1;

        else
            col[sudoku[j][c] - 1] = 1;
    }
    return c;
}

void *ChunkRunner(void *param)
{
    thread_data *thread = (thread_data *)param;

    // Row check
    for (int i = thread->start_row; i < thread->start_row + thread->nrows; i++)
    {
        bool isValid = (rowCheck(i) != -1);

        auto now = chrono::system_clock::now(); // Record timestamp
        long long timestamp = chrono::duration_cast<chrono::nanoseconds>(now.time_since_epoch()).count() - base_timestamp;

        if (!isValid)
        {
            string s = "Thread " + to_string(thread->thread_id) + " found an error in row " + to_string(i) + " " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
            thread->terminate = true;
            pthread_exit(0);
        }
        else
        {
            string s = "Thread " + to_string(thread->thread_id) + " checks row " + to_string(i) + " and is valid " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
        }
    }

    // Column check
    for (int i = thread->start_col; i < thread->start_col + thread->ncols; i++)
    {
        bool isValid = (colCheck(i) != -1);

        auto now = chrono::system_clock::now();
        long long timestamp = chrono::duration_cast<chrono::nanoseconds>(now.time_since_epoch()).count() - base_timestamp;

        if (!isValid)
        {
            string s = "Thread " + to_string(thread->thread_id) + " found an error in column " + to_string(i) + " " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
            thread->terminate = true;
            pthread_exit(0);
        }
        else
        {
            string s = "Thread " + to_string(thread->thread_id) + " checks column " + to_string(i) + " and is valid " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
        }
    }

    // Subgrid check
    for (int i = thread->start_sub; i < thread->start_sub + thread->nsubs; i++)
    {
        bool isValid = (subCheck(i) != -1);

        auto now = chrono::system_clock::now();
        long long timestamp = chrono::duration_cast<chrono::nanoseconds>(now.time_since_epoch()).count() - base_timestamp;

        if (!isValid)
        {
            string s = "Thread " + to_string(thread->thread_id) + " found an error in subgrid " + to_string(i) + " " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
            thread->terminate = true;
            pthread_exit(0);
        }
        else
        {
            string s = "Thread " + to_string(thread->thread_id) + " checks subgrid " + to_string(i) + " and is valid " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
        }
    }
    pthread_exit(0);
}

void *CyclicRunner(void *param)
{
    thread_data *thread = (thread_data *)param;

    // Row check
    int count = 0;
    for (int i = thread->start_row; i < N && count++ < thread->nrows; i += K)
    {
        bool isValid = (rowCheck(i) != -1);

        auto now = chrono::system_clock::now();
        long long timestamp = chrono::duration_cast<chrono::nanoseconds>(now.time_since_epoch()).count() - base_timestamp;

        if (!isValid)
        {
            string s = "Thread " + to_string(thread->thread_id) + " found an error in row " + to_string(i) + " " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
            thread->terminate = true;
            pthread_exit(0);
        }
        else
        {
            string s = "Thread " + to_string(thread->thread_id) + " checks row " + to_string(i) + " and is valid " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
        }
    }

    // Column check
    count = 0;
    for (int i = thread->start_col; i < N && count++ < thread->ncols; i += K)
    {
        bool isValid = (colCheck(i) != -1);

        auto now = chrono::system_clock::now();
        long long timestamp = chrono::duration_cast<chrono::nanoseconds>(now.time_since_epoch()).count() - base_timestamp;

        if (!isValid)
        {
            string s = "Thread " + to_string(thread->thread_id) + " found an error in column " + to_string(i) + " " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
            thread->terminate = true;
            pthread_exit(0);
        }
        else
        {
            string s = "Thread " + to_string(thread->thread_id) + " checks column " + to_string(i) + " and is valid " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
        }
    }

    // Subgrid check
    count = 0;
    for (int i = thread->start_sub; i < N && count++ < thread->nsubs; i += K)
    {
        bool isValid = (subCheck(i) != -1);

        auto now = chrono::system_clock::now();
        long long timestamp = chrono::duration_cast<chrono::nanoseconds>(now.time_since_epoch()).count() - base_timestamp;

        if (!isValid)
        {
            string s = "Thread " + to_string(thread->thread_id) + " found an error in subgrid " + to_string(i) + " " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
            thread->terminate = true;
            pthread_exit(0);
        }
        else
        {
            string s = "Thread " + to_string(thread->thread_id) + " checks subgrid " + to_string(i) + " and is valid " + to_string(timestamp) + "\n";
            Buffers[thread->thread_id] += s;
        }
    }

    pthread_exit(0);
}

bool readInputFromFile(const string &filename)
{
    ifstream inputFile(filename);
    if (!inputFile)
    {
        cout << "Error: Could not open file " << filename << endl;
        return false;
    }

    inputFile >> K >> N;

    int sq_root = static_cast<int>(sqrt(N));
    if (sq_root * sq_root != N)
    {
        cout << "Error: N must be a perfect square." << endl;
        return false;
    }

    sudoku.resize(N, vector<int>(N));
    for (int i = 0; i < N; i++)
    {
        for (int j = 0; j < N; j++)
            inputFile >> sudoku[i][j];
    }

    // cout << "Input Sudoku:" << endl;
    // for (int i = 0; i < N; i++)
    // {
    //     for (int j = 0; j < N; j++)
    //         cout << sudoku[i][j] << " ";

    //     cout << endl;
    // }

    inputFile.close();
    return true;
}

vector<string> splitByNewline(const string &buffer)
{
    vector<string> lines;
    int start = 0, end;

    while ((end = buffer.find('\n', start)) != string::npos)
    {
        string line = buffer.substr(start, end - start);
        if (!line.empty())
        {
            lines.push_back(line);
        }
        start = end + 1;
    }

    if (start < buffer.size())
        lines.push_back(buffer.substr(start));

    return lines;
}
void writeOutputToFile(const string &output)
{
    ofstream outFile(output_filename, ios::app);
    if (outFile)
        outFile << output << endl;

    else
        cout << "Error: Could not open output file." << endl;

    outFile.close();
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
                string logMessage = line.substr(0, lastSpace);           // Log message
                long long timestamp = stoll(line.substr(lastSpace + 1)); // Timestamp
                logs.emplace_back(timestamp, logMessage);                // Add to the vector
            }
        }
    }

    sort(logs.begin(), logs.end(), [](const pair<long long, string> &a, const pair<long long, string> &b)
         { return a.first < b.first; });

    for (const auto &log : logs)
    {
        string s = log.second + " " + to_string(log.first);
        writeOutputToFile(s);
    }
}

void sequentialRunner()
{
    bool isValid = true;
    for (int i = 0; i < N; i++)
    {
        if (rowCheck(i) == -1 || colCheck(i) == -1 || subCheck(i) == -1)
            break;
    }

    string result = isValid ? "Sudoku is valid." : "Sudoku is invalid.";
    writeOutputToFile(result);
}

int main(int argc, char *argv[])
{
    if (argc > 2 && strcmp(argv[2], "1") == 0)
    {
        use_cyclic = true;
    }
    else if (argc > 2 && strcmp(argv[2], "2") == 0)
    {
        use_sequential = true;
    }
    if (!readInputFromFile(argv[1]))
    {
        return 1;
    }

    if (use_sequential)
    {
        auto start_time = chrono::high_resolution_clock::now();
        sequentialRunner();
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::microseconds>(end_time - start_time).count();
        cout << "The total time taken by sequential method is " << duration << " microseconds" << endl;
        return 0;
    }

    ofstream clearFile(output_filename, ios::out);
    clearFile.close();

    auto start_time = chrono::high_resolution_clock::now();
    base_timestamp = chrono::duration_cast<chrono::nanoseconds>(start_time.time_since_epoch()).count();

    pthread_t threads[K];
    thread_data *thdata[K];

    Buffers.resize(K, "");

    int n = N / K;
    int remaining = N % K;

    for (int i = 0; i < K; i++)
    {
        thdata[i] = new thread_data();
        thdata[i]->thread_id = i;
        thdata[i]->nrows = n;
        thdata[i]->ncols = n;
        thdata[i]->nsubs = n;
        thdata[i]->terminate = false;
    }
    for (int i = 0; i < remaining; i++)
    {
        thdata[i]->nrows++;
        thdata[i]->ncols++;
        thdata[i]->nsubs++;
    }

    if (!use_cyclic)
    {
        // Chunk method
        thdata[0]->start_row = 0;
        thdata[0]->start_col = 0;
        thdata[0]->start_sub = 0;

        for (int i = 1; i < K; i++)
        {
            thdata[i]->start_row = thdata[i - 1]->start_row + thdata[i - 1]->nrows;
            thdata[i]->start_col = thdata[i - 1]->start_col + thdata[i - 1]->ncols;
            thdata[i]->start_sub = thdata[i - 1]->start_sub + thdata[i - 1]->nsubs;
        }
        for (int i = 0; i < K; i++)
            pthread_create(&threads[i], NULL, ChunkRunner, (void *)thdata[i]);
    }
    else
    {
        // cyclic method
        for (int i = 0; i < K; i++)
        {
            thdata[i]->start_row = i;
            thdata[i]->start_col = i;
            thdata[i]->start_sub = i;
        }
        for (int i = 0; i < K; i++)
            pthread_create(&threads[i], NULL, CyclicRunner, (void *)thdata[i]);
    }

    for (int i = 0; i < K; i++)
        pthread_join(threads[i], NULL);

    bool isValid = true;
    for (int i = 0; i < K; i++)
    {
        if (thdata[i]->terminate)
        {
            isValid = false;
            break;
        }
    }
    auto end_time = chrono::high_resolution_clock::now();
    parseAndWriteLogs(Buffers);

    string result = isValid ? "Sudoku is valid.\n" : "Sudoku is invalid.\n";
    writeOutputToFile(result);

    auto duration = chrono::duration_cast<chrono::microseconds>(end_time - start_time).count();

    writeOutputToFile("The total time taken is " + to_string(duration) + " microseconds.\n");

    if (use_cyclic)
        cout << "The total time taken by cyclic method is " << duration << " microseconds" << endl;
    if (!use_cyclic)
        cout << "The total time taken by chunk method is " << duration << " microseconds" << endl;

    for (int i = 0; i < K; i++)
    {
        delete thdata[i];
    }

    return 0;
}
