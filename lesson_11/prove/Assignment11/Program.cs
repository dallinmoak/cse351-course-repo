using System.Collections.Generic;
using System.Diagnostics;
using System.Threading;

namespace assignment11;

// should follow the boss-worker pattern

public class Assignment11
{
    private const long START_NUMBER = 10_000_000_000;
    private const int RANGE_COUNT = 1_000_000;

    static Queue<long> numbersQueue = new Queue<long>();
    static object lockForQueue = new object();

    private static bool IsPrime(long n)
    {
        if (n <= 3)
            return n > 1;
        if (n % 2 == 0 || n % 3 == 0)
            return false;

        for (long i = 5; i * i <= n; i = i + 6)
        {
            if (n % i == 0 || n % (i + 2) == 0)
                return false;
        }
        return true;
    }

    public static void Main(string[] args)
    {
        int numbersProcessed = 0;
        int primeCount = 0;

        Console.WriteLine("Prime numbers found:");

        var stopwatch = Stopwatch.StartNew();

        for (long i = START_NUMBER; i < START_NUMBER + RANGE_COUNT; i++)
        {
            numbersQueue.Enqueue(i);
        }

        List<Thread> workers = new List<Thread>();
        int workerCount = 10;

        for (int i = 0; i < workerCount; i++)
        {
            Thread t = new Thread(() =>
            {
                while (true)
                {
                    int numberToProcess;
                    lock (lockForQueue)
                    {
                        if (numbersQueue.Count == 0)
                        {
                            break;
                        }
                        numberToProcess = (int)numbersQueue.Dequeue();
                    }
                    Interlocked.Increment(ref numbersProcessed);
                    if (IsPrime(numberToProcess))
                    {
                        Interlocked.Increment(ref primeCount);
                        Console.Write($"{numberToProcess}, ");
                    }
                }
            });
            workers.Add(t);
            t.Start();
        }

        foreach (Thread t in workers)
        {
            t.Join();
        }

        // for (long i = START_NUMBER; i < START_NUMBER + RANGE_COUNT; i++)
        // {
        //     numbersProcessed++;
        //     if (IsPrime(i))
        //     {
        //         primeCount++;
        //         Console.Write($"{i}, ");
        //     }
        // }

        stopwatch.Stop();

        Console.WriteLine();
        Console.WriteLine();

        // Should find 43427 primes for range_count = 1000000
        Console.WriteLine($"Numbers processed = {numbersProcessed}");
        Console.WriteLine($"Primes found      = {primeCount}");
        Console.WriteLine($"Total time        = {stopwatch.Elapsed}");
    }
}
