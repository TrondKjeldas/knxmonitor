from sys import argv

try:
    module_to_run = argv[1]

    argv = argv[1:]

    exec "from %s import main2" % module_to_run

except Exception as e:
    print "Error: %s" % e
    print "usage: 'python -m knxmonitor <filename>'"
    print "        the function 'main' in the specified file will be run"

main2(argv)
