project('procon_kyogi', 'cpp',
  version: '0.1.0',
  default_options: ['cpp_std=c++20'])

ver = meson.project_version()

deps = [
  dependency('gl'),
  dependency('glfw3'),
  dependency('glew'),
  dependency('glm'),
]

src = [
  'src/simulator.cpp',
  'src/solve1.cpp',
  'src/solve2.cpp',
  'src/solveList2.cpp',
  'src/display.cpp',
]

procon_kyogi = executable('simulator', src,
  dependencies: deps,
  install: true)
