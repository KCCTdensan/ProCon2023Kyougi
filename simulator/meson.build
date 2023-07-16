project('procon_kyogi', 'cpp',
  version: '0.1.0',
  default_options: ['cpp_std=c++20'])

ver = meson.project_version()

GUI_boolean = true

if GUI_boolean
  deps = [
    dependency('gl'),
    dependency('glfw3'),
    dependency('glew'),
    dependency('glm'),
  ]
else
  deps = []
endif

src = [
  'src/simulator.cpp',
  'src/solve1.cpp',
  'src/solve2.cpp',
  'src/solveList2.cpp',
]
if GUI_boolean
  src += 'src/display.cpp'
endif

procon_kyogi = executable('simulator', src,
  dependencies: deps,
  install: true)
