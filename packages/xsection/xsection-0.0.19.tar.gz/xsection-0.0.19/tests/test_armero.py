from xsection.library import Rectangle, Channel


if __name__ == "__main__":
    # From Armero's full report, Table 1 on page 87
    rectangle = [
    #    t/h         J             Jw        Jv               Js
        [1.0,  2.25416620e4, 8.66423278e3,  4.12500467e3, 2.94805924e4],
        [0.5,  4.58455629e3, 2.03297383e4,  3.74877704e3, 1.58209907e5],
        [0.1,  5.02809625e1, 4.25107929e2,  1.29638570e3, 1.67786200e2]
    ]
    for tr, J, Jw, Jv, Js in rectangle:
        s = Rectangle(d=20, b=tr*20, mesh_scale=1/60)
        print(" ", (s._analysis.torsion_constant()-J)/J)
        print(" ", (s.cww()[0,0]-Jw)/Jw)
        print(" ", (s.cvv()[0,0]-Jv)/Jv)
#       print(s.summary())

    #
    # Channel
    #
    channel = [
    #    t/h      xsc           J             Jw
        [0.10, 2.28811887, 8.50099503e+1, 1.87665937e4],
        [0.05, 2.59689539, 3.19982170e-1, 4.42779462e3],
        [0.01, 2.78436565, 9.53031691e-2, 3.03596030e3]
    ]

    for tr, xsc, J, Jw, in channel:
        print(f"Channel<t/h={tr}>")
        s = Channel(d=20, b=0.4*20, tf=tr*20, tw=tr*20, mesh_scale=1/800)
        s = s.translate(s._analysis.shear_center())
        print(" ", (s._analysis.torsion_constant()-J)/J)
        print(" ", (s.cww()[0,0]-Jw)/Jw)

    print(s.summary())
