import hou

def submit(node):
    print(type(node))
    print(node.parms())
    print(node.parm("job_name"))
    job_name = node.parm("job_name").evalAsString()
    output_driver = node.parm("output_driver").evalAsString()
    print(type(job_name))
    print(type(output_driver))
    start = node.parm("f1").eval()
    end = node.parm("f2").eval()
    increment = node.parm("f3").eval()
