#!/bin/bash

install_lib() {
  yum -y upgrade
  yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel mysql-devel readline-devel tk-devel gcc make libffi-devel python3-devel
}

install_python() {
  python3 -V | grep 'Python 3.8.6'
  if [ $? == 0 ]; then
    return
  fi

  if [ ! -d Python-3.8.6 ];then
    if [ ! -f Python-3.8.6.tar.xz ];then
      wget https://www.python.org/ftp/python/3.8.6/Python-3.8.6.tar.xz
    else
      tar -xf Python-3.8.6.tar.xz
    fi
  fi

  cd Python-3.8.6
  ./configure prefix=/usr/local/python3 --enable-shared
  make && make install
  echo "/usr/local/python3/lib/" >> /etc/ld.so.conf
  ldconfig
  ln -sf /usr/local/python3/bin/python3.8 /usr/bin/python3
}

install_python_requirement() {
  python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
  python3 -m pip install -q -r ${project_dir}/requirements/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ln -sf /usr/local/python3/bin/pyinstaller /usr/bin/pyinstaller
}

compile() {
  echo -e "\033[32mStart Compile JumpServer script...\033[0m"
  cd ${project_dir}
  pyinstaller ${project_dir}/main.py --log-level ERROR --hidden-import=redis --clean --distpath ./pkg
  rm -rf ${project_dir}/build
  echo -e "\033[32mCompile Success...\033[0m"
}

collect_static() {
  echo -e "\033[32mStart Collect Static Files...\033[0m"
  base_dir=${project_dir}/pkg/main
  task_dir=${base_dir}/package/tasks/
  static_dir=${base_dir}/package/static/
  mkdir -p $task_dir $static_dir
  cp -rf ${project_dir}/package/tasks/* ${task_dir}
  cp -rf ${project_dir}/package/static/* ${static_dir}
  echo -e "\033[32mCollect Static Files Success...\033[0m"
}

tar_bin() {
  cd ${project_dir}
  tar cf ${project_dir}/jms_inspect.tar jms_inspect_cli pkg
  # rm -rf pkg && rm -rf jms_inspect_cli
  echo ""
  echo -e "\033[32mSuccess...\033[0m"
  echo -e "\033[32mScript path: ↓ ↓ ↓ ↓ ↓\033[0m"
  echo -e "\033[32m${project_dir}/jms_inspect.tar\033[0m"
  echo ""
}

install() {
  set -e  # exit on any error
  project_dir=$(cd "$(dirname "$0")";cd ..;pwd)
  install_lib
  install_python
  install_python_requirement
  compile
  collect_static
  tar_bin
  }

install
