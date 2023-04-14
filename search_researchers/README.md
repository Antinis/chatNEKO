# Retrieve Researchers on Google Scholar


This is a Python crawler for querying and retrieving information about researchers from Google Scholar based on their affiliations and research interests. The crawler uses the [scholarly](https://github.com/scholarly-python-package/scholarly) package, which is a Python wrapper for the Google Scholar API.

The script will automatically search for researchers based on the specified affiliations and research interests and save the results in `.xls` format.
Command line arguments include:

* `--orgs`: The organizations to search for researchers (separated by comma).
* `--no_proxy`: Whether to use a proxy or not (use --no_proxy to disable using a proxy).
* `--http_proxy`: The HTTP proxy address (e.g., 127.0.0.1:1080).
* `--https_proxy`: The HTTPS proxy address (e.g., 127.0.0.1:1080).
* `--interests`: The research fields to search for (separated by comma).
* `--min_cit`: The minimum number of citations required for a researcher to be included in the results.
* `--not_save`: Do not save results

Here is an example command:

    python Retrive.py --orgs zju,tokyo --interests Computer_Vision,Machine_Learning --min_cit 10000

This command will search for researchers from orgnizations related to `zju` and `tokyo`that have interests in Computer Vision and Machine Learning and have a minimum of 10000 citations.

The result is:

```
Searching Zhejiang University...
Start  Time:  2023-04-14 22:33:08
Elapse Time:  0:00:24.757999
Found 7 in 105
-----------------------------------------------------------------------------------------------------------------------
           Name                                         Affiliation                           Interests  citedby(10000)
0  Chunhua Shen                                 Zhejiang University  computer vision & machine learning         52737.0
1       Yi Yang                                 Zhejiang University  computer vision & machine learning         52314.0
2    Xiaofei He  Professor of Computer Science, Zhejiang University  computer vision & machine learning         37391.0
3      Deng Cai  Professor of Computer Science, Zhejiang University  computer vision & machine learning         32536.0
4        Fei Wu  Professor of Computer Science, Zhejiang University                    machine learning         17275.0
5  Wenguan Wang                                 Zhejiang University                     computer vision         12551.0
6     Hujun Bao                                 Zhejiang University                     computer vision         12214.0




Searching University of Tokyo...
Start  Time:  2023-04-14 22:33:35
Elapse Time:  0:00:47.894835
Found 6 in 207
-------------------------------------------------------------------------------------------------------------------------------------------------------
               Name                                                                                       Affiliation         Interests  citedby(10000)
0    Sanmay Ganguly  Project Assistant Professor, International Center for Elementary Particle Physics - University …  machine learning        177733.0
1  Masashi Sugiyama         Director, RIKEN Center for Advanced Intelligence Project / Professor, The University of …  machine learning         28814.0
2  Katsushi Ikeuchi                                                           Emeritus professor, University of Tokyo   computer vision         28497.0
3        Koji Tsuda                                                          Professor, GSFS, The University of Tokyo  machine learning         16808.0
4       Yoichi Sato                               Professor, Institute of Industrial Science, The University of Tokyo   computer vision         14068.0
5   Kiyoharu Aizawa                                                                               University of Tokyo   computer vision         12299.0



Zhejiang University
Chunhua Shen & Yi Yang & Xiaofei He & Deng Cai & Fei Wu & Wenguan Wang & Hujun Bao

University of Tokyo
Sanmay Ganguly & Masashi Sugiyama & Katsushi Ikeuchi & Koji Tsuda & Yoichi Sato & Kiyoharu Aizawa



```