## openplotter-kplex

OpenPlotter app to manage kplex devices

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Install dependencies:
Download kplex from http://www.stripydog.com/kplex/download.html

`dpkg -i ./kplex_1.x-x_xxx.deb`

Clone the repository:

`git clone https://github.com/openplotter/openplotter-kplex`

Make your changes and create the package:

```
cd openplotter-kplex
dpkg-buildpackage -b
```

Install the package:

```
cd ..
sudo dpkg -i openplotter-kplex_x.x.x-xxx_all.deb
```

Run post-installation script:

`sudo kplexPostInstall`

Run:

`openplotter-kplex`

Make your changes and repeat package, installation and post-installation steps to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://cloudsmith.io/~openplotter/repos/openplotter/packages/).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1