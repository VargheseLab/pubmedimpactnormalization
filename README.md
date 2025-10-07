# PubMed Impact Normalization
This repository contains the code and docker container for the [JMIR paper](https://www.jmir.org/2025/1/e60616). It provides a webserver to view and analyze the (normalized) PubMed-Statistics over the years using a query- and reference-term.

Visit [pmcounts.diz-ag.med.ovgu.de](https://pmcounts.diz-ag.med.ovgu.de/)` for an online version.

### Local installation using docker
The local container allows several additional settings, such if you have a personal API-Key.

    docker pull ghcr.io/vargheselab/pubmedimpactnormalization:main
    docker run --rm -p 8080:8080 -v pubmedimpactnormalization_volume:/instance pubmedimpactnormalization:main
    Open Webbrowser with 127.0.0.1:8080

## Citation

Varghese J, Bickmann L, Strünker T, Neuhaus N, Tüttelmann F, Sandmann S
Publication Counts in Context: Normalization Using Query and Reference Terms in PubMed
J Med Internet Res 2025;27:e60616
URL: https://www.jmir.org/2025/1/e60616
DOI: 10.2196/60616
