## openplotter-kplex

OpenPlotter app to manage NMEA 0183 data

### Installing

#### For production

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **production** and install this app from *OpenPlotter Apps* tab.

#### For development

Install [openplotter-settings](https://github.com/openplotter/openplotter-settings) for **development**.

Install openplotter-kplex dependencies:

`sudo apt install gpsd gpsd-clients kplex`

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

Make your changes and repeat package, installation and post-installation steps to test. Pull request your changes to github and we will check and add them to the next version of the [Debian package](https://launchpad.net/~openplotter/+archive/ubuntu/openplotter).

### Documentation

https://openplotter.readthedocs.io

### Support

http://forum.openmarine.net/forumdisplay.php?fid=1