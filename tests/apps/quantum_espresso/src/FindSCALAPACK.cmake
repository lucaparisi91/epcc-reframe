find_package(PkgConfig)
pkg_check_modules(libsci_mpiREQUIRED libsci_mpi)

if ( ${LIBSCI_MPI_FOUND}  )
  message("Found libsci_mpi: ${LIBSCI_MPI_LDFLAGS}")
  set(SCALAPACK_FOUND TRUE)
  set(SCALAPACK_LIBRARIES ${LIBSCI_MPI_LDFLAGS})
  set(SCALAPACK_LINKER_FLAGS "")
else()
  set(SCALAPACK_FOUND FALSE)
endif()