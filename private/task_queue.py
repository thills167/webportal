import time
from rpy2.robjects.packages import importr
import rpy2.robjects as ro

#Import appropriate R packages
xcms = importr("xcms")
rann = importr("RANN")

while True:
   
    pending = db(db.task.status == 0).select().first()
    if not pending:
        continue
    tid = pending.id    
    print 'pending *********'+ str(tid)+'***********\n'
    peaks = ""

    #Peak Detection begins
    detectmethod = pending.peak_detection_method
    set = xcms.xcmsSet

    if detectmethod == '0':
        try:
            print 'Enter values for all Cent Wave peak detection procedure parameter'
            pd = "centWave"
            ppmvalue = pending.ppm
            a=pending.min_peak_width
            b=pending.max_peak_width
            vec = ro.FloatVector([a,b])
            peaks=set("/home/lavya/Downloads/testdataforxcms/",method=pd,ppm=ppmvalue,peakwidth=vec)
            print "finished."
        except:
            print

    elif detectmethod == '1'    :
        try:
            print 'Enter values for all Matched filter peak detection procedure parameter'
            fwhmvalue = pending.fwhm
            stepsize = pending.step_size
            pd = "matchedFilter"
            peaks=set("/home/lavya/Downloads/testdataforxcms",method=pd,fwhm=fwhmvalue,step=stepsize)
            print "Matched Filter finishes"
        except:
            print

    #Peak Detection Ends here.

    #Alignment begins ...
    findGroup = xcms.group
    alignments = ""

    alignmethod = pending.alignment_method
    print alignmethod

    if alignmethod == '0':
        try:
            print 'Enter values for peak alignment using density procedure'
            mzwidvalue = pending.mzwid
            minfracvalue = pending.minfrac
            bwvalue = pending.bw
            alignments = findGroup(peaks, method="density",mzwid=mzwidvalue,minfrac=minfracvalue,bw=bwvalue)
            print 'alignment finished.'
        except:
            print 

    elif alignmethod == '1':
        try:
           alignments = findGroup(peaks, method="mzClust")
        except:
            print

    elif alignmethod == '2':
        try:
            alignments = findGroup(peaks, method="nearest")
        except:
            print

    print 'ALIGNMENTS *******: '+str(alignments)
    #Peak Alignment ends here.

    #Retention time correction starts ..
    #save plot as jpeg and Retention time correction
    pyretcor=xcms.retcor

    retcormethod = pending.retention_time_method
    print retcormethod
    
    savePlot = "/home/lavya/web2py/applications/volt/uploads/ "+str(tid)+".jpg"
    pyjpeg = ro.r('jpeg')
    pyjpeg(savePlot)

    # 0 is peak groups
    if retcormethod == '0':
        peakgroupmethod = pending.peak_groups_method
        # 0 is for LOESS and 1 is for linear
        if peakgroupmethod == '0':
            try:
                rts=pyretcor(alignments,smooth="loess",family="symmetric",plottype="mdevden")
                print 'peak group & loess'
            except:
                print 
        elif peakgroupmethod == '1':
            try:
                print ''
                rts=pyretcor(alignments,smooth="linear",family="symmetric",plottype="mdevden")
                print 'peak group & linear'
            except:
                print

    elif retcormethod == '1':
        try:
            rts=pyretcor(alignments,method="obiwarp",plottype="deviation")
            print 'obiwarp'
        except:
            print

    pydevoff = ro.r('dev.off')
    pydevoff()
    
    #db.sample_files.insert(sample=6,file_name="cw-den-obi-out",file="/home/lavya/web2py/applications/volt/uploads/ "+detectmethod+"-"+alignmethod+"-"+retcormethod+".jpg")
  
    db(db.task.id == pending.id).update(status=2)
    db.commit()
