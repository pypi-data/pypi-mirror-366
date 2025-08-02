// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_PARALLEL_HPP
#define MLHP_CORE_PARALLEL_HPP

#include "mlhp/core/config.hpp"
#include "mlhp/core/coreexport.hpp"

#ifdef MLHP_MULTITHREADING_OMP
#include <omp.h>
#endif

namespace mlhp::parallel
{

#ifdef MLHP_MULTITHREADING_OMP
    using Lock = omp_lock_t;
#else
    using Lock = std::uint8_t;
#endif

MLHP_EXPORT 
size_t getMaxNumberOfThreads( );

MLHP_EXPORT 
size_t getNumberOfThreads( );

MLHP_EXPORT 
void setNumberOfThreads( size_t nthreads );

MLHP_EXPORT 
size_t getThreadNum( );

MLHP_EXPORT 
void initialize( Lock& lock );

MLHP_EXPORT 
void aquire( Lock& lock );

MLHP_EXPORT 
void release( Lock& lock );

} // namespace mlhp::parallel

#endif // MLHP_CORE_PARALLEL_HPP
