#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <cmath>
#include <pthread.h>
#include <atomic>
#include <algorithm>

using namespace std;
using namespace std::chrono;


string output_filename = "output.txt";
vector<vector<int>> sudoku;
int K,N,taskInc;
bool rowCheck(int r)
{
    vector<int> row(N, 0);
    for (int j = 0; j < N; j++)
    {
        int val = sudoku[r][j];
        if (val < 1 || val > N || row[val - 1] == 1)
            return false;
        row[val - 1] = 1;
    }
    return true;
}

bool colCheck(int c)
{
    vector<int> col(N, 0);
    for (int i = 0; i < N; i++)
    {
        int val = sudoku[i][c];
        if (val < 1 || val > N || col[val - 1] == 1)
            return false;
        col[val - 1] = 1;
    }
    return true;
}

bool subCheck(int s)
{
    int n = sqrt(N);
    if (n * n != N)
    {
        cerr << "Error: N must be a perfect square." << endl;
        return false;
    }
    vector<int> sub(N, 0);
    int r = (s / n) * n;
    int c = (s % n) * n;
    for (int i = r; i < r + n; i++)
    {
        for (int j = c; j < c + n; j++)
        {
            int val = sudoku[i][j];
            if (val < 1 || val > N || sub[val - 1] == 1)
                return false;
            sub[val - 1] = 1;
        }
    }
    return true;
}

void sequentialRunner()
{
    bool isValid = true;
    for (int i = 0; i < N; i++)
    {
        if (rowCheck(i) == -1 || colCheck(i) == -1 || subCheck(i) == -1)
            break;
    }
}

bool readInputFromFile(const string &filename)
{
    ifstream inputFile(filename);
    if (!inputFile)
    {
        cout << "Error: Could not open file " << filename << endl;
        return false;
    }
    inputFile >> K >> N >> taskInc;
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
    inputFile.close();
    return true;
}

int main(int argc, char *argv[])
{
    if (!readInputFromFile(argv[1]))
    {
        return 1;
    }
    ofstream clearFile(output_filename, ios::out);
    clearFile.close();
    auto start_time = high_resolution_clock::now();
    sequentialRunner();
    auto end_time = high_resolution_clock::now();
    auto totalDuration = duration_cast<nanoseconds>(end_time - start_time).count();
    cout << "The total time taken is " << totalDuration << " nanoseconds." << endl;
    return 0;
}
