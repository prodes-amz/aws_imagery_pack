<img src="aws.png" width="64">

# AWS imagery pack (aws_imagery_pack)
Due to the great convenience of having a data cube available in AWS repositories (Sentinel, Landsat, and others), this library aims to offer a simple operator for searching and downloading orbital images, using only one area of interest (file. geojson), and a range of dates of interest.

The resources offered by the AWS API, offers download of each item broken down by the [SAFE format](https://earth.esa.int/web/sentinel/user-guides/sentinel-1-sar/data-formats/sar-formats). However, it does not offer the compressed format (.zip) or the complete download of the SAFE folder. Therefore, this script is an adaptation for the assembly of the SAFE folder item by item, ending with the compression of the final folder.

**All modules available here are under construction. Therefore, many errors and malfunctions can occur.**

1. [Setting up your environment](#1-Setting-up-your-environment)
2. [Prepare your virtual environment](#2-Prepare-your-virtual-environment)
3. [Examples ](#3-Examples)
4. [TODO-list](#4-TODO-list)

# Setting up your environment

## Python version and OS
The `aws_imagery_pack` was developed using Python version 3.7+, and Linux 19.10 eoan operational system. 

## Preparing your `.env` file

This library uses decoupling, which demands you to set up variables that is only presented locally, for instance, 
the path you want to save something, or the resources of your project. In summary, your environment variables. So, 
copy a paste the file `.env-example` and rename it to `.env`. Afterwards, just fill out each of the variables content 
within the file:

```
USER_SENTINEL_HUB = SENTINEL_HUB_USER
PASS_SENTINEL_HUB = SENTINEL_HUB_PASS

DATASET_PATH=ROOT_PATH_TO_DATA
LOCAL_TMP_BUCKET=PATH_TO_TMP_FOLDER
```

# Prepare your virtual environment
First of all, check if you have installed the libraries needed:
```
sudo apt-get install python3-env
```
then, in the
```
python -m venv .venv
```
and activates it:
```
source .venv/bin/activate
```
as soon you have it done, you are ready to install the requirements.

## Installing `requirements.txt`
```
pip install -r requirements.txt
```

## Sentinel hub account
If you do not have an Sentinel-hub account, sign in [here](https://www.sentinel-hub.com/explore/eobrowser).

## AWS account and credentials
After to sign in, launch a simple EC2 instance (if you are not familiar with AWS features, read more about it [here](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)). Inside this instance, you will need to clone this repository, as well as the setup of aws credentials. 

To download your credentials, check the following steps:
1. Open the IAM console.
1. From the navigation menu, click Users.
1. Select your IAM user name.
1. Click User Actions, and then click Manage Access Keys.
1. Click Create Access Key.
1. Your keys will look something like this:
    * Access key ID example: AKIAIOSFODNN7EXAMPLE
    * Secret access key example: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
1. Click Download Credentials, and store the keys in a secure location. Normally in:
```
~/.aws/
```

## Access your EC2 using SSH protocol
To do things a bit more easier, I would recommend access your instance via SSH protocol. To do so, first, download your authentication `.pem` (Privacy Enhanced Mail) file and place it in some safe folder in your local machine. This file consists in your private key. Do not lose this! :) 

**[Please, read this article to learn how to generate your authentication keys](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)** 

So, in your local machine terminal, type:

```ssh -i your/path/to/file.pem awsuser@IP_OF_EC2_INSTANCE```

and, that is all! 

# Examples 

## Copying from AWS S3 bucket to your S3 bucket
The basic search settings, thresholds and values were concentrated in the `settings.py` file. To establish new conditions, this file must be revised.

So, to search for Sentinel-1 images, using only VV and VH polarization, your `settings.py` will have these parameters (beside other, of course):
```
SENTINEL_1_PARAMS = {
    'bucket': 'sentinel-s1-l1c',
    'platformname': 'Sentinel-1',
    'producttype': 'GRD',
    'sensoroperationalmode': 'IW',
    'polarisationmode': ['VV', 'VH'],
    'images_limit': 10
}
```
the `images_limit` is a key to limit the number of images per AOI. If everything is ok, try the following command:
```
python aws_main.py -ranges 2020-01-01 2020-01-13 -verbose True
```
then, you should see something like:
```
[2020-04-23 18:13:33] {aws_main.py    :21  } INFO : Starting process... 
[2020-04-23 18:13:33] {aws_process.py :21  } INFO : >> 1 AOIs (in .geojson format) found! 
[2020-04-23 18:13:33] {aws_process.py :24  } INFO : >> Range date: 2020-01-01 to 2020-01-13 - AOI: data/aoi/aoi_1.geojson 
[2020-04-23 18:13:33] {aws_search.py  :56  } INFO : >>>> Searching in 100 rows [pagination]... 
[2020-04-23 18:13:36] {aws_process.py :38  } INFO : >>>>>> 20 images found! 
[2020-04-23 18:13:36] {aws_process.py :45  } WARNING: >>>>>> There is a limit of 10 images per AOI (data/aoi/aoi_1.geojson) and range dates ('2020-01-01', '2020-01-13'). Thus, only 10 from 20 will be used! 
[2020-04-23 18:13:36] {aws_download.py:287 } INFO : >> Copying the 10 repository content from sentinel-s1-l1c to data/tmp/... 
[2020-04-23 18:13:36] {aws_download.py:296 } INFO : >>>> Copying item 1. S1B_IW_GRDH_1SDV_20200113T225227_20200113T225252_019804_025724_767B... 
...
```

You can also copy the images not to your instances, but (of course) to a S3 bucket! You will just need to set your `LOCAL_TMP_BUCKET` with your storage address. For example, `LOCAL_TMP_BUCKET='s3://sentinel-s1-tmp/'`. 

## Copying from AWS S3 bucket to your local filesystem
The script can also be used to search and download images to your computer, without using EC2 instances. To do so, set your `LOCAL_TMP_BUCKET` variable. In this case, a download is performed, instead of a copy. 

# TODO-list
Well, this source-code is being released only for personal tests, but also to help out who probably has similar needs. 
For this reason, we have a lot to do in terms of unit tests, python conventions, optimization issues, refactoring, 
so on! So, Feel free to use and any recommendation will be totally welcome! 

**Enjoy it!**  





