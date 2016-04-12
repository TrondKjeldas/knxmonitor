from sys import argv
import cProfile

try:
    module_to_run = argv[1]

    argv = argv[1:]

    exec "from %s import main2" % module_to_run

except Exception as e:
    print "Error: %s" % e
    print "usage: 'python -m knxmonitor <filename>'"
    print "        the function 'main' in the specified file will be run"

#cProfile.run('main2(argv)', None, 'cumtime')
main2(argv)
