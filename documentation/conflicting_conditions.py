from diagrams import Cluster, Diagram, Edge
from diagrams.c4 import C4Node

# import ctypes  # An included library with Python install.
# def Mbox(title, text, style):
#     return ctypes.windll.user32.MessageBoxW(0, text, title, style)

# result = Mbox('Your title', 'Your text', 1)
# print(result)


with Diagram("Realtionships between conditions", show=False):
    with Cluster("Hard constraints"):
        h11 = C4Node("H11", "", "Maximum shifts of specific type (night)", "constraint")
        h10 = C4Node("H10", "", "Single assignment per day - exception", "constraint")
        h9 = C4Node("H9", "", "Minimal continuous free period", "constraint")
        h12 = C4Node("H12", "", "Planned vacation", "constraint")
        h7 = C4Node("H7", "", "Maximum incomplete week-ends", "constraint")
        h6 = C4Node("H6", "", "Consecutive days off", "constraint")
        h5 = C4Node("H5", "", "Consecutive assignments", "constraint")
        h8 = C4Node("H8", "", "Total assignments", "constraint")
        h3 = C4Node("H3", "", "Shift type successions", "constraint")
        h2 = C4Node("H2", "", "Under-staffing", "constraint")
        h4 = C4Node("H4", "", "Missing required skill", "constraint")
        h1 = C4Node("H1", "", "Single assignment per day", "constraint")

    with Cluster("Soft constraints"):
        s9 = C4Node("S9", "", "Overtime preferences", "constraint")
        s8 = C4Node("S8", "", 'Using "if needed" skill', "constraint")
        s7 = C4Node("S7", "", "Total working weekends - optimal", "constraint")
        s6 = C4Node("S6", "", "Total assignments - optimal ", "constraint")
        s5 = C4Node("S5", "", "Complete week-end optimal", "constraint")
        s4 = C4Node("S4", "", "Assignement preferences", "constraint")
        s3 = C4Node("S3", "", "Consecutive days off - optimal", "constraint")
        s2 = C4Node("S2", "", "Consecutive assignments - optimal", "constraint")
        s1 = C4Node("S1", "", "Insufficient staffing for optimal coverage", "constraint")

    h9 >> Edge(style="curved", label="possibly contradicts") << h6
    h1 >> Edge(style="curved", label="overrides") << h10
    h2 >> Edge(style="curved", label="affects") >> s1
    h5 >> Edge(style="curved", label="affects") >> s2
    h6 >> Edge(style="curved", label="affects") >> s3
    h8 >> Edge(style="curved", label="affects") >> s6
    h8 >> Edge(style="curved", label="affects") >> s9
    s6 >> Edge(style="curved", label="affects") << s9
    
