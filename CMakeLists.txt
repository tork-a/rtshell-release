project(rtshell)
cmake_minimum_required(VERSION 2.8)

if(EXISTS "/etc/debian_version")
  set(SETUPTOOLS_ARG_EXTRA "--install-layout=deb")
else()
  set(SETUPTOOLS_ARG_EXTRA "")
endif()

add_custom_target(compile_rtshell ALL
  COMMAND python setup.py build
  WORKING_DIRECTORY ${PROJECT_SOURCE_DIR})

add_custom_target(install_rtshell
  COMMAND python setup.py install --prefix=${CMAKE_INSTALL_PREFIX} ${SETUPTOOLS_ARG_EXTRA} --root=/$(DESTDIR) --skip-build
  WORKING_DIRECTORY ${PROJECT_SOURCE_DIR})

install(CODE "execute_process(COMMAND \"${CMAKE_COMMAND}\" --build \"${CMAKE_BINARY_DIR}\" --target install_rtshell)")
install(FILES package.xml DESTINATION share/rtshell/)
string(REGEX MATCH "catkin" need_catkin "$ENV{_}")
if(need_catkin)
  install(CODE "
## this is tricky force write catkin marker file
set(_catkin_marker_file \"\${CMAKE_INSTALL_PREFIX}/.catkin\")
# check if the develspace marker file exists yet
if(EXISTS \${_catkin_marker_file})
  file(READ \${_catkin_marker_file} _existing_sourcespaces)
  if(_existing_sourcespaces STREQUAL \"\")
    # write this sourcespace to the marker file
    file(WRITE \${_catkin_marker_file} \"${CMAKE_INSTALL_PREFIX}/${CATKIN_PACKAGE_SHARE_DESTINATION}\")
  else()
    # append to existing list of sourcespaces if it's not in the list
    list(FIND _existing_sourcespaces \"${CMAKE_INSTALL_PREFIX}/${CATKIN_PACKAGE_SHARE_DESTINATION}\" _existing_sourcespace_index)
    if(_existing_sourcespace_index EQUAL -1)
      file(APPEND \${_catkin_marker_file} \";${CMAKE_INSTALL_PREFIX}/${CATKIN_PACKAGE_SHARE_DESTINATION}\")
    endif()
  endif()
else()
  # create a new develspace marker file
  # NOTE: extra care must be taken when running multiple catkin jobs in parallel
  #       so that this does not overwrite the result of a similar call in another package
  file(WRITE \${_catkin_marker_file} \"${CMAKE_INSTALL_PREFIX}/${CATKIN_PACKAGE_SHARE_DESTINATION}\")
endif()
")
endif()
