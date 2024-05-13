from diagrams import Cluster, Diagram, Edge
from diagrams.c4 import C4Node

# import ctypes  # An included library with Python install.
# def Mbox(title, text, style):
#     return ctypes.windll.user32.MessageBoxW(0, text, title, style)

# result = Mbox('Your title', 'Your text', 1)
# print(result)


with Diagram("Realtionships between conditions", show=False):
    with Cluster("Hard constraints"):
        h12 = C4Node("HC12", "", "Planned vacation", "constraint")
        h11 = C4Node("HC11", "", "Maximum shifts of specific type (night)", "constraint")
        # h11 = C4Node("HC11", "", "Missing required skill - exception", "constraint")
        h10 = C4Node("HC10", "", "Single assignment per day - exception", "constraint")
        h9 = C4Node("HC9", "", "Minimal continuous free period", "constraint")
        h8 = C4Node("HC8", "", "Total assignments", "constraint")
        h7 = C4Node("HC7", "", "Maximum incomplete week-ends", "constraint")
        h6 = C4Node("HC6", "", "Consecutive days off", "constraint")
        h5 = C4Node("HC5", "", "Consecutive assignments", "constraint")
        h4 = C4Node("HC4", "", "Missing required skill", "constraint")
        h3 = C4Node("HC3", "", "Shift type successions", "constraint")
        h2 = C4Node("HC2", "", "Under-staffing", "constraint")
        h1 = C4Node("HC1", "", "Single assignment per day", "constraint")

    with Cluster("Soft constraints"):
        s9 = C4Node("SC9", "", "Overtime preferences", "constraint")
        s8 = C4Node("SC8", "", 'Using "if needed" skill', "constraint")
        s7 = C4Node("SC7", "", "Total working weekends - optimal", "constraint")
        s6 = C4Node("SC6", "", "Total assignments - optimal ", "constraint")
        s5 = C4Node("SC5", "", "Complete week-end optimal", "constraint")
        s4 = C4Node("SC4", "", "Assignement preferences", "constraint")
        s3 = C4Node("SC3", "", "Consecutive days off - optimal", "constraint")
        s2 = C4Node("SC2", "", "Consecutive assignments - optimal", "constraint")
        s1 = C4Node("SC1", "", "Insufficient staffing for optimal coverage", "constraint")

    # user >> frontend >> backend
    # h4 >> Edge(label="overrides") << h11 >> Edge(label="implies") >> s7
    h1 >> Edge(label="overrides") << h10
    h2 >> Edge(label="affects") >> s1
    h5 >> Edge(label="affects") >> s2
    h6 >> Edge(label="affects") >> s3
    h8 >> Edge(label="affects") >> s6
    h8 >> Edge(label="affects") >> s9
    s6 >> Edge(label="affects") << s9
    h12 >> Edge(label="possibly contradicts") << h8
    h9 >> Edge(label="possibly contradicts") << h6
    
