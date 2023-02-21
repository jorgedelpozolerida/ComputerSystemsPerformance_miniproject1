#include <iostream>
#include "includes/utils.hpp"
#include <string.h>
#include <thread>
#include <vector>
#include <chrono>
#include <fstream>

const int INPUT_SIZE = 200000;
const int MAX_NUM_THREADS = 8;
const int MAX_HASH_BITS = 18;

// u64 is defined in utils.hpp - it is an alias for usigned long long
u64 *generate_input()
{
    u64 *generated = new u64[INPUT_SIZE];
    srand(INPUT_SIZE); // set a seed

    for (int i = 0; i < INPUT_SIZE; i++)
    {
        generated[i] = (((u64)RAND() << 48) ^ ((u64)RAND() << 35) ^ ((u64)RAND() << 22) ^
                        ((u64)RAND() << 9) ^ ((u64)RAND() >> 4));
    }

    return generated;
}

// we might want to pass the buffer by reference
void process_partition(u64 *data, int start, int end, int hash_bits, std::vector<std::vector<std::tuple<u64, u64>>> buffer)
{
    for (size_t i = start; i < end; i++)
    {
        int hash = utils::hash(data[i], hash_bits);
        std::tuple<int, u64> t = std::make_tuple(hash, data[i]);
        // std::cout << "(" << hash << ", " << data[i] << ")\n";

        buffer.at(hash).push_back(t);
    }
}

double run_experiment(int hash_bits, int num_threads)
{
    u64 *input = generate_input();
    const int partition_size = INPUT_SIZE / num_threads;

    std::cout << "Threads: " << num_threads << "\n";

    std::vector<std::thread> threads;
    std::vector<std::vector<std::vector<std::tuple<u64, u64>>>> thread_buffers;

    for (int i = 0; i < num_threads; ++i)
    {
        std::vector<std::vector<std::tuple<u64, u64>>> output_buffer;

        // create "partitions"
        int max_partition_hash = utils::max_partition_hash(hash_bits);
        for (size_t i = 0; i <= max_partition_hash; i++)
        {
            std::vector<std::tuple<u64, u64>> partition_buffer;
            output_buffer.push_back(partition_buffer);
        }

        // set which thread processes what part of the data
        size_t start = i * partition_size;
        size_t end = (i + 1) * partition_size;
        if (i == num_threads - 1)
        {
            end = INPUT_SIZE;
        }

        // create the thread
        std::thread thread(process_partition, input, start, end, hash_bits, output_buffer);
        threads.push_back(std::move(thread));
    }

    // measuring the time
    auto start = std::chrono::steady_clock::now();
    for (std::thread &thread : threads)
    {
        thread.join();
    }
    auto end = std::chrono::steady_clock::now();
    std::chrono::duration<double> elapsed_seconds = end - start;

    delete input;
    return elapsed_seconds.count();
}

int main()
{
    for (int experiment = 1; experiment <= 8; experiment += 1)
    {
        std::fstream fout;

        // Create a new file to store updated data

        std::string filename = "Project1/experiments/independent_output/experiment_" + std::to_string(experiment) + ".csv"; // Assumed to be executed in /home/group_ivas/ComputerSystemsPerformance
        fout.open(filename, std::ios::out);

        fout << "Threads;Hash_Bits;Running Time\n";

        for (int hash_bits = 1; hash_bits <= MAX_HASH_BITS; hash_bits += 1) 
        {
            std::cout << " HASH BITS: " << hash_bits <<"\n";

            for (int num_threads = 1; num_threads <= MAX_NUM_THREADS; num_threads *= 2) 
            {
                double exp = run_experiment(hash_bits, num_threads);

                fout << num_threads << ";" << hash_bits << ";" << exp << "\n";
            }
        }  

        fout.close();
    }
}