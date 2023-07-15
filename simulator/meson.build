project('procon_kyogi', 'cpp',
  version: '0.1.0',
  default_options: ['cpp_std=c++20'])

ver = meson.project_version()

src = [
  'src/simulator.cpp',
  'src/solve1.cpp',
  'src/solve2.cpp',
  'src/solveList2.cpp'
]

inc = include_directories('include')

procon_kyogi = executable('example', src,
  include_directories: inc,
  install: true)