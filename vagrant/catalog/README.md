# Udacity Full Stack Web Developer Nanodegree Catalog Application Project

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Intro](#intro)
- [Environment Installation](#environment-installation)
- [Instructions](#instructions)
- [Endpoint Structure](#endpoint-structure)

## Intro
On the surface, the Catalog Item application is a web application that stores items based on categories for easy reference.

What is running the application though is a relational mySQL database using the python framework Flask with SQLAlchemy.

Third party signin provider Google has also been added to the application to illustrate user authentication.

## Environment Installation

### Install VirtualBox

VirtualBox is the software that actually runs the virtual machine. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) Install the _platform package_ for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.

Currently (October 2017), the supported version of VirtualBox to install is version 5.1. Newer versions do not work with the current release of Vagrant.

**Ubuntu users:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center instead. Due to a reported bug, installing VirtualBox from the site may uninstall other software you need.

### Install Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. [Download it from vagrantup.com.](https://www.vagrantup.com/downloads.html) Install the version for your operating system.

**Windows users:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

![vagrant --version](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/584881ee_screen-shot-2016-12-07-at-13.40.43/screen-shot-2016-12-07-at-13.40.43.png)

_If Vagrant is successfully installed, you will be able to run_ `vagrant --version`
_in your terminal to see the version number._
_The shell prompt in your terminal may differ. Here, the_ `$` _sign is the shell prompt._

### Download the VM configuration

Use Github to fork and clone, or download, the repository [https://github.com/udacity/fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm).

You will end up with a new directory containing the VM files. Change to this directory in your terminal with `cd`. Inside, you will find another directory called **vagrant**. Change directory to the **vagrant** directory:

![vagrant-directory](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/58487f12_screen-shot-2016-12-07-at-13.28.31/screen-shot-2016-12-07-at-13.28.31.png)

_Navigating to the FSND-Virtual-Machine directory and listing the files in it._
_This picture was taken on a Mac, but the commands will look the same on Git Bash on Windows._

## Instructions

### Start the virtual machine

From your terminal, inside the **vagrant** subdirectory, run the command `vagrant up`. This will cause Vagrant to download the Linux operating system and install it. This may take quite a while (many minutes) depending on how fast your Internet connection is.

![vagrant-up-start](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/58488603_screen-shot-2016-12-07-at-13.57.50/screen-shot-2016-12-07-at-13.57.50.png)

_Starting the Ubuntu Linux installation with `vagrant up`._
_This screenshot shows just the beginning of many, many pages of output in a lot of colors._

When `vagrant up` is finished running, you will get your shell prompt back. At this point, you can run `vagrant ssh` to log in to your newly installed Linux VM!

![linux-vm-login](https://d17h27t6h515a5.cloudfront.net/topher/2016/December/58488962_screen-shot-2016-12-07-at-14.12.29/screen-shot-2016-12-07-at-14.12.29.png)

_Logging into the Linux VM with `vagrant ssh`._

### Install the database

Once you `vagrant ssh` into your virtual, go to the catalog application by running

```cd /vagrant/cataglog```

Then run the script `python3 database_setup.py`

Next, if you want data already populated in the application run `python3 populate_db.py`

### Creating an application configuration
Flask allows for you to create an application config in an instance folder in your application.

So add the following directory to the catalog application `/catalog/instance`

Next, create a file in the new folder called `/catalog/application.cfg`

In `application.cfg`, add the following lines:

```
SECRET_KEY=YOUR SUPER SECRET KEY
DEBUG=True
```

### Starting your application

Once your database has been created and the configuration file, run the following command `python3 application.py`

You should be now able to go to `http://localhost:5000` and view the landing page of your application.

### Logging into the application

NOTE: In-order to see the sign-in functionality, you need to create a google api account and do the following:

- Download the `client_secrets.json` file and add it to the root of the application.
- Update the `client_id` in `templates/login.html`

## Endpoint Structure
Here are the json data structures available for the application.

### Individual Item

```
/category/<int:category_id>/item/<int:item_id>/json

Item	
  category_id   Integer
  description   String
  id    Integer
  name    String
```

### Category Items

```
/category/<int:category_id>/items/json

CategoryItems	
  0	
    category_id   Integer
    description   String
    id    Integer
    name    String
``` 
