<!-- omit in toc -->
# Project Scotch
*Matching User Chess Games with GM Games to Learn Stronger Continuations*

This repository contains a series of classes, a Cython implementation of the Longest Common Sequence (LCS) algorithm, and a partition Parquet directory full of Grandmaster chess games, which work in tandem to help users understand how their games would've been continued by the most notable players in chess. 

<!-- omit in toc -->
## Table of Contents

- [Introduction](#introduction)
- [Classes](#classes)
- [Cython Implementation of LCS](#cython-implementation-of-lcs)
- [Data](#data)
  - [Parquet](#parquet)
  - [Dask](#dask)
  - [ThreadPoolExecutor](#threadpoolexecutor)
- [Setup and Usage](#setup-and-usage)
- [Authors and Acknowledgements](#authors-and-acknowledgements)
- [License](#license)
- [References](#references)

## Introduction

Project Scotch is an innovative chess analytics tool designed to help users study and improve their chess gameplay by comparing their games to a database of Grandmaster-level games. The tool processes a large dataset of over 7 million chess positions from professional tournament games, sourced from [PGN Mentor](pgnmentor.com). By submitting their own chess game, users can have it matched against the database, enabling them to follow and study a closely resembling game played by a Grandmaster. This unique approach provides users with a deeper understanding of their own gameplay and offers insights on how to learn from the best of the best.

The project is built on a range of carefully crafted and documented components, which are designed to create an informative and interactive experience for chess learners. Its Position class, utilizing efficient bitboards, serves as the foundation for analyzing chess positions. These positions are generated through a Parser class, which bridges the user's game and the tool by processing PGN files and extracting necessary metadata for integration with other components. From there, the submitted game is run through Matcher, which identifies the best matching games from the database based on the longest sequence of matching moves, offering users the opportunity to learn from top-level players. The Navigator class then handles the visual representation of the match, allowing users to step through positions and gain insights into their gameplay.

These components work together to form a cohesive system that helps users explore and learn from a wealth of Grandmaster-level chess games, enhancing their understanding of the game and supporting their progress towards mastery. 

In short, this program's methodologies include:
- Efficient data storage using the [Parquet](https://parquet.apache.org) file format
- Parallel processing of large datasets using [Dask](https://docs.dask.org) partitions
- Longest Common Subsequence (LCS) algorithm optimized with [Cython](https://cython.readthedocs.io)
- User-friendly game navigation and visualization using [tkinter](https://docs.python.org/3/library/tkinter.html)

## Classes

- **Parser**: Serves as a bridge between the user's game and the internal workings of the tool. It ingests the PGN file provided by the user and extracts crucial information, such as positions and metadata.
- **Position**: At the heart of the program, it takes minimal information supplied by chess programs and extends that format with as much context about legal moves as possible. Utilizes bitboards for more efficient operations and game state visualization.
- **Matcher**: Draws meaningful connections between the user's game and the vast database of existing GM games. Identifies the best matching game based on the longest sequence of matching moves.
- **Navigator**: Provides a visual representation of the game, allowing users to walk through each position step by step with key bindings and dynamic labels.
- **Utilities**: Sits in the background and provides essential functions that facilitate smooth operation across all components.

Each class file in this project contains a docstring outlining the attributes and methods that the class requires and handles.

## Cython Implementation of LCS

This module contains an optimized implementation of the Longest Common Subsequence (LCS) algorithm using [Cython](https://cython.readthedocs.io). The purpose of this optimization is to improve the performance of the LCS calculation when working with large sequences. Cython is a powerful tool that allows us to generate C code from Python-like source code, leading to faster execution times. This is achieved through the use of Cython's cpdef function declaration, typed memory views, and native C data types, reudcing Python's overhead.

The Cython implementation is meant to be used as an imported module in other Python scripts that require an efficient LCS algorithm. To use this module, simply import it into your script and call the `lcs_indices` function with your input sequences as NumPy arrays with `dtype = np.int64`. The function will return a tuple containing the length of the LCS and a list of two tuples, where each tuple contains the start and end indices of the LCS in the short and long sequences.

## Data

The program processes a large dataset containing over 7 million chess positions from professional tournament games as of May 2023. The source material for this dataset comes from [PGN Mentor](pgnmentor.com), a popular resource for chess games in the PGN (Portable Game Notation) format.

### Parquet
[Parquet](https://parquet.apache.org) is a columnar storage file format optimized for big data processing frameworks like Apache Spark, Apache Hive, and Apache Impala. It is designed to provide efficient data compression and encoding schemes, enabling fast querying of data stored in a columnar fashion. By using the Parquet format, the program can reduce storage space and improve query performance when working with the large dataset of chess positions.

### Dask
[Dask](https://docs.dask.org) is a parallel computing library for Python that enables users to work with larger-than-memory datasets efficiently. It can automatically parallelize operations on large datasets, breaking them into smaller chunks and executing tasks concurrently. This allows for efficient processing and manipulation of large datasets without running into memory constraints.

In this program, Dask is used to partition the large dataset of chess positions into smaller, more manageable pieces. This partitioning enables the program to perform operations on the dataset in parallel, significantly improving performance and reducing execution time. By using Dask in conjunction with the Parquet file format, the program can efficiently read and write data in parallel, allowing for faster processing of the large dataset.

### ThreadPoolExecutor

[ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor) is a high-level interface for asynchronously executing functions using a pool of worker threads. It is part of the `concurrent.futures` module in Python and provides an efficient way to manage and parallelize tasks, improving the overall performance of the program.

In the Matcher class, the ThreadPoolExecutor is used to concurrently process multiple games from the dataset. By distributing the tasks across multiple threads, the program can leverage parallelism to speed up the matching process. This allows for faster identification of the best matching games, even when working with a large dataset containing millions of chess positions.

## Setup and Usage

Project Scotch is a Python implementation that utilizes five classes, an Application file, and a Cython module. It is designed to be run directly from the terminal. To set up the project and use it, follow these steps:

1. Install [Python](https://www.python.org/downloads/).
2. Install the required packages by running the following command in your terminal: `pip install cython numpy pandas dask[complete] pyarrow chess alive-progress tkinter`
   - **Note**: You might need to install [tkinter](https://docs.python.org/3/library/tkinter.html) separately based on your system. For example, in Ubuntu, you can run `sudo apt-get install python3-tk`.
3. Clone this repository to your local machine.
4. In the terminal, navigate to the repository's directory.
5. Run the main Application file using Python, with the following options:
   
Supply a PGN game as a command-line argument:
```
python Application.py /path/to/your/game.pgn
```

Run the application without any arguments to open a file dialog for submitting your own game:
```
python Application.py
```

If no game is submitted, a demo will run.

## Authors and Acknowledgements

This project was developed by [James Parkington](https://github.com/jparkington)

It was shaped under the supervision of [Professor Lindsay Jamieson](https://roux.northeastern.edu/people/lindsay-jamieson/) during class *5001 - Intensive Foundations of Computer Science* at the **Roux Institute of Northeastern University**.

I would like to express my gratitude to Professor Jamieson for her guidance and excellent feedback throughout this project, as well as my classmates for their valuable input and collaboration.

## License

This project is not subject to any specific licensing. The data provided, PGN Mentor, has its own terms of use, which can be found on their website.

## References

- [PGN Mentor](https://www.pgnmentor.com/)
- [Cython Documentation](https://cython.readthedocs.io/)
- [Dask Documentation](https://docs.dask.org/)
- [Parquet File Format](https://parquet.apache.org/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor)
- [Chess Library for Python](https://python-chess.readthedocs.io/en/latest/)
- [Alive Progress Bar](https://github.com/rsalmei/alive-progress)