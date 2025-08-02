# XBOINC

## Python package for submitting track simulations in particle accelerators with BOINC system

## INSTRUCTIONS FOR WINDOWS:

### How to install boinc client/manager on Windows

Use the installer at: https://boinc.berkeley.edu/download.php


### Compile boinc api and examples from source on Windows

We use MSys2, in particular **MINGW64**

Follow the instruction at https://www.msys2.org to install MSYS2 and GCC:
```
pacman -S mingw-w64-x86_64-gcc
pacman -Suy
pacman -Suy  # you need indeed twice!
```

Install git and python packages:
```
pacman -S git
pacman -Sy mingw-w64-x86_64-python-numpy
pacman -Sy mingw-w64-x86_64-python-scipy
pacman -Sy mingw-w64-x86_64-python-pandas
pacman -Sy mingw-w64-x86_64-python-pip
pacman -Sy mingw-w64-x86_64-python-wheel
pacman -Sy vim
```

#### Compile BOINC
```
pacman -S autotools
cd
git clone https://github.com/BOINC/boinc
cd boinc
export BOINC_DIR=$PWD
 
./_autosetup
 
./configure --disable-server --disable-client --disable-manager --disable-gui
# This one takes very long
 
make
# This also takes quite long
```

### Generate xboinc source and input files on windows

```
cd 
mkdir xsuite_packages
cd xsuite_packages
git clone https://github.com/xsuite/xobjects.git
git clone https://github.com/xsuite/xpart.git
git clone https://github.com/xsuite/xtrack.git
git clone https://github.com/xsuite/xfields.git
git clone https://github.com/xsuite/xboinc.git

pip install --no-deps --no-build-isolation -e xtrack
pip install --no-deps --no-build-isolation -e xobjects
pip install --no-deps --no-build-isolation -e xpart
pip install --no-deps --no-build-isolation -e xfields
pip install --no-deps --no-build-isolation -e xboinc
```

#### Compile and generate input


```bash
cd xboinc/examples/000_build_executable
python 000_build_executable.py
bash 001msys2_compile_executable.sh
cd ../002_lhc
python 001_build_input.py
cd ../003_boinc
echo $BOINC_DIR # Check if points into the BOINC source directory 
python 000_build_executable.py
make
```

#### Run/test the executable
```
cp ../002_lhc/xboinc_input.bin .
chmod +x xboinc_executable
./xboinc_executable
```

#### Running the test application with boinc server
We still work in MSYS2 (MINGW64)

In order to have it working we needed to have the file structure in C:\PrgramData\Boinc

```
cd /c/ProgramData/BOINC # This in WINDOWS is hidden
cp ~/xsuite_packages/xboinc/examples/003_boinc/client_state_save.xml .
```
then

```
nano account_test.xml 
```

write
```
<account>
    <master_url>http://test.test</master_url>
    <project_name>test_project</project_name>
</account>
```
then 
```nano cc_config.xml```
write
```
<cc_config>
    <options>
        <skip_cpu_benchmarks/>
        <unsigned_apps_ok/>
    </options>
</cc_config>
```
Then make folder structure
```
mkdir projects/test.test
cp ~/xsuite_packages/xboinc/examples/002_lhc/xboinc_input.bin projects/test.test/input.bin
cp ~/xsuite_packages/xboinc/examples/003_boinc/xboinc_executable.exe projects/test.test/xboinc_executable
```

In one terminal:
`cp client_state_save.xml client_state.xml; ./../../Program\ Files/BOINC/boinc.exe`

In another:
`/c/Program\ Files/BOINC/boincmgr.exe`

In case of problems stop boing client in the status bar:

<img width="427" alt="image" src="https://user-images.githubusercontent.com/8049893/191972091-13fee31a-9dc8-459e-9f3f-3224c09bec47.png">

You can suspend using the activity menu:

<img width="785" alt="image" src="https://user-images.githubusercontent.com/8049893/191973210-64e0c156-9565-41d9-9e8c-8e5eeef19b2b.png">

You can see the checkpoints in:

<img width="835" alt="image" src="https://user-images.githubusercontent.com/8049893/191973307-498ce522-7542-4975-9e18-702bf449abd3.png">

You can restart from the same menu. 


When the job is finished, the result are saved in "projects/test.test/output.bin"


## INSTRUCTIONS FOR UBUNTU:

### How to install boinc client/manager on Ubuntu
https://boinc.berkeley.edu/wiki/Installing_BOINC_on_Ubuntu

Basically only:
```
sudo apt-get install aptitude
sudo aptitude install boinc-client boinc-manager
```
#### Compile boinc api and examples from source on Ubuntu

On a fresh ubuntu installation I neede to:

```
sudo apt install make
sudo apt install m4
sudo apt install pkg-config
sudo apt install autoconf
sudo apt install libtool
sudo apt install g++
```

```
cd
git clone https://github.com/BOINC/boinc
cd boinc
export BOINC_DIR=$PWD
./_autosetup
```
From 
https://boinc.berkeley.edu/trac/wiki/BuildSystem

"If you're developing or porting a BOINC application, you need only the API: "
```
./configure --disable-server --disable-client --disable-manager --disable-gui
# This one takes very long
```
and then
```
make
# This also takes quite long
```

### Installing xsuite packages
```
cd
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source miniconda3/bin/activate
pip install numpy scipy matplotlib pandas ipython pytest
mkdir xsuite_packages
cd xsuite_packages

git clone https://github.com/xsuite/xobjects
git clone https://github.com/xsuite/xdeps
git clone https://github.com/xsuite/xpart
git clone https://github.com/xsuite/xtrack
git clone https://github.com/xsuite/xfields
git clone https://github.com/xsuite/xboinc

pip install -e xobjects
pip install -e xdeps
pip install -e xpart
pip install -e xtrack
pip install -e xfields
pip install -e xboinc
```

#### Compile and generate input

```bash
cd xboinc/examples/000_build_executable
python 000_build_executable.py
bash 001msys2_compile_executable.sh
cd ../002_lhc
python 001_build_input.py
cd ../003_boinc
echo $BOINC_DIR # Check if points into the BOINC source directory 
python 000_build_executable.py
make
```

#### Run/test the executable
```
cp ../002_lhc/xboinc_input.bin .
chmod +x xboinc_executable
./xboinc_executable
```

### Running the test application with boinc server
```
cd
mkdir xboinc_test
cp ~/xsuite_packages/xboinc/examples/003_boinc/client_state_save.xml .
```
then

```
vim account_test.xml 
```

write
```
<account>
    <master_url>http://test.test</master_url>
    <project_name>test_project</project_name>
</account>
```
then 
```vim cc_config.xml```
write
```
<cc_config>
    <options>
        <skip_cpu_benchmarks/>
        <unsigned_apps_ok/>
    </options>
</cc_config>
```

Add the same GUI RPC passwords in
```
vim gui_rpc_auth.cfg
```
and in
```
vim /etc/boinc-client/gui_rpc_auth.cfg
```

Then make folder structure
```
mkdir projects/test.test
cp ~/xsuite_packages/xboinc/examples/002_lhc/xboinc_input.bin projects/test.test/input.bin
cp ~/xsuite_packages/xboinc/examples/003_boinc/xboinc_executable.exe projects/test.test/xboinc_executable
```

In one terminal:
`cp client_state_save.xml client_state.xml; boinc --gui_rpc_port 31417`

In another:
`boincmgr --gui_rpc_port 31417`

!! Before running BOINC client or manager, kill the previous BOINC session
```
sudo /etc/init.d/boinc-client stop
```
