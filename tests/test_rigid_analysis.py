import pyslammer as slam

motions = slam.sample_ground_motions()  # Load all sample ground motions
for motion in motions:
    print(motion)
