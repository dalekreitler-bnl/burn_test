import math
import subprocess
import os
import argparse
import burn_test
import numpy

parser = argparse.ArgumentParser()
parser.add_argument('-N',
                    '--N_shells',
                    metavar='N',
                    type=int,
                    help='Number of resolution shells')
parser.add_argument('-d',
                    '--detector_distance',
                    metavar='d',
                    type=float,
                    help='Detector distance in millimeters')

parser.add_argument('-p',
                    '--plot_type',
                    metavar='p',
                    type=str,
                    help='plot intensity, spots, or spots_no_ice',
                    default='intensity')

parser.add_argument('-f',
                    '--fast',
                    metavar='f',
                    type=bool,
                    help='skip generate file step',
                    default=False)

args = parser.parse_args()

def main():
    print("=====================================\n"
          +"Input equal area shells: " + str(args.N_shells))
    print("Input det. distance (mm): " + str(args.detector_distance))
    print("Input plot type: " + args.plot_type)
    plots = burn_test.MakePlots(data_type=args.plot_type)
    if not args.fast:
        plots.generate_files()

    plots.make_plots()
    h=burn_test.get_half_intensity_frame_no('burn_test_all_res.csv')
    l=burn_test.get_half_spot_frame_no('burn_test_all_res.csv')
    z=burn_test.get_half_spot_no_ice_frame_no('burn_test_all_res.csv')
    print("================================\n"+
          "Burn rate stats\n"+
          "================================\n"+           
          "\nIntensities fall below 0.5*I0 at frame no.: "+str(h))
    print("Spots fall below 0.5*N0 at frame no.: "+str(l))
    print("Spots (ice filtered) fall below 0.5*N0 at frame no.: "+str(z)+"\n")
    plots.parse_plot_fit_logs()

if __name__ == "__main__":
    main()

class Experiment_params:

	def __init__(self,
                 detector_distance = 120.0,
                 wavelength = 0.92,
                 exposure_time = 0.005,
                 d_min=1.6,
                 N_shells = 10):
            self.detector_distance = detector_distance
            self.wavelength=wavelength
            self.exposure_time = exposure_time #seconds
            self.d_min = d_min #Angstroms
            self.N_shells = N_shells

	def print_experiment_params(self):
		print("Detector Distance (mm): " + str(self.detector_distance))
		print("Wavelength (A): " + str(self.wavelength))
		print("Exposure time (sec): " + str(self.exposure_time))
		print("No. of shells: " + str(self.N_shells))

	def get_shell_bounds(self):

		shell_bounds = [10000]

		d_min_in_mm = self.resolution_to_dist_from_center(self.d_min)

		for k in range(1,self.N_shells+1):
			
			r = d_min_in_mm*math.sqrt(float(k)/self.N_shells)
			shell_bounds.append(self.dist_from_center_to_resolution(r))

		return shell_bounds


	def dist_from_center_to_resolution(self,
					   dist_from_center):
		if dist_from_center == 0:
			d = 1000
		else:
			d = self.wavelength / (2*math.sin(0.5*math.atan(dist_from_center/self.detector_distance)))

		return d #Angstroms


	def resolution_to_dist_from_center(self,
					   resolution):

		_dist_from_center = self.detector_distance*math.tan(2*math.asin(self.wavelength/(2*resolution)))

		return _dist_from_center #mm from detector center

	def get_high_res_limits(self):
		
		shell_bounds = self.get_shell_bounds()		

		d_max = shell_bounds[self.N_shells]
		d_min = shell_bounds[self.N_shells - 1]

		high_res_limits = [d_min,d_max]

		return high_res_limits

	def get_low_res_limits(self):

		shell_bounds = self.get_shell_bounds()

		d_max = shell_bounds[1]
		d_min = shell_bounds[0]

		low_res_limits = [d_min,d_max]

		return low_res_limits

class MakeFiles:
    
    def __init__(self,
                N_shells=10,
                detector_distance=120.0):

            run_find_spots_all_res()
            self.d_min = get_d_min()
            self.N_shells = N_shells
            self.detector_distance = detector_distance
            self.current_params = Experiment_params(N_shells = self.N_shells,
                                                    detector_distance = self.detector_distance,
						    d_min = self.d_min)
            self.run_find_spots_high_res()
            self.run_find_spots_low_res()
            trim_high_res()

    def run_find_spots_high_res(self):
        high_res_limits = self.current_params.get_high_res_limits()

	print(high_res_limits)
        command_1 = "/usr/local/crys-local/phenix-1.17.1-3660/build/bin/dials.find_spots_client"
        command_2 = " spotfinder.filter.d_min={}".format(high_res_limits[1])
        command_3 = " spotfinder.filter.d_max={}".format(high_res_limits[0])
	command_4 = " spotfinder.threshold.xds.sigma_background=2.0"
        command_5 = " $PWD/../*2.cbf > burn_test_high_res.log"
        subprocess.call(command_1+command_2+command_3+command_4+command_5, shell=True)
        subprocess.call("$PWD/../passxmltocsv.bash burn_test_high_res.log > burn_test_high_res.csv", shell=True)
        return

    def run_find_spots_low_res(self):
        low_res_limits = self.current_params.get_low_res_limits()
        command_1 = "/usr/local/crys-local/phenix-1.17.1-3660/build/bin/dials.find_spots_client"
        command_2 = " spotfinder.filter.d_min={}".format(low_res_limits[1])
        command_3 = " spotfinder.filter.d_max={}".format(low_res_limits[0])
        command_4 = " $PWD/../*2.cbf > burn_test_all_res.log"
        subprocess.call(command_1+command_2+command_3+command_4, shell=True)
	subprocess.call("$PWD/../passxmltocsv.bash burn_test_all_res.log > burn_test_all_res.csv", shell=True)
	return

class MakePlots:

    def __init__(self, N_shells=10, detector_distance=120.0, data_type='intensity'):
        self.N_shells = N_shells
        self.detector_distance = detector_distance
        self.data_type = data_type
        self.get_data_type_int()

    def get_data_type_int(self):

        data_type_dict = {"spots" : 1, "spots_no_ice" : 2, "intensity" : 6}
        self.data_type_int = data_type_dict[self.data_type]
	return

    def generate_files(self):
        self.fileObject = MakeFiles(N_shells=self.N_shells, detector_distance = self.detector_distance)
        return

    def parse_plot_fit_logs(self):
	print("Slope of log({}) vs. Frame no.".format(self.data_type))
        pipe = subprocess.Popen("cat *{}.fit | grep \"m               = -\"".format(self.data_type), shell=True, stdin=subprocess.PIPE)
        os.waitpid(pipe.pid,0)
        return

    def make_plots(self):
	self.plot_all_res()
        self.plot_all_res_fit()
	self.plot_high_res()
        self.plot_high_res_fit()
        return

    def plot_all_res(self):
        pipe = subprocess.Popen('gnuplot -p',shell=True,stdin=subprocess.PIPE)
        pipe.stdin.write("set datafile separator \',\'\n")
        pipe.stdin.write("set xlabel \'Frame No.\'\n")
        pipe.stdin.write("set ylabel \'({})\'\n".format(self.data_type))
        pipe.stdin.write("set output \'all_res_{}.png\'\n".format(self.data_type))
        pipe.stdin.write("plot \'burn_test_all_res.csv\' using 1:{}\n".format(self.data_type_int+1))
        pipe.stdin.write("plot \'burn_test_all_res.csv\' using 1:{}\n".format(self.data_type_int+1))
        pipe.stdin.write('quit\n')
        os.waitpid(pipe.pid,0)
        return

    def plot_all_res_fit(self):
        #subprocess.call("gnuplot -p all_res.gnuplot > all_res.fit", shell=True)
        pipe = subprocess.Popen('gnuplot -p',shell=True,stdin=subprocess.PIPE)
        pipe.stdin.write("set datafile separator \',\'\n")
        pipe.stdin.write("f(x) = m*x + b\n")
        pipe.stdin.write("set fit logfile \'burn_all_res_{}.fit\'\n".format(self.data_type))
        pipe.stdin.write("fit f(x) \'burn_test_all_res.csv\' using 1:(log(${})) via m,b\n".format(self.data_type_int+1))
        pipe.stdin.write("set xlabel \'Frame No.\'\n")
        pipe.stdin.write("set ylabel \'LOG({})\'\n".format(self.data_type))
        pipe.stdin.write("set output \'all_res_fit_{}.png\'\n".format(self.data_type))
        pipe.stdin.write("plot \'burn_test_all_res.csv\' using 1:(log(${})), f(x)\n".format(self.data_type_int+1))
        pipe.stdin.write("plot \'burn_test_all_res.csv\' using 1:(log(${})), f(x)\n".format(self.data_type_int+1))
        pipe.stdin.write('quit\n')
        os.waitpid(pipe.pid,0)
        return

    def plot_high_res(self):
        #subprocess.call("gnuplot -p high_res.gnuplot > high_res.fit", shell=True)
        pipe = subprocess.Popen('gnuplot -p',shell=True,stdin=subprocess.PIPE)
        pipe.stdin.write("set datafile separator \',\'\n")
        pipe.stdin.write("set xlabel \'Frame No.\'\n")
        pipe.stdin.write("set ylabel \'({})\'\n".format(self.data_type))
        pipe.stdin.write("set output \'high_res_{}.png\'\n".format(self.data_type))
        pipe.stdin.write("plot \'burn_test_high_res.csv\' using 1:{}\n".format(self.data_type_int+1))
        pipe.stdin.write("plot \'burn_test_high_res.csv\' using 1:{}\n".format(self.data_type_int+1))
        pipe.stdin.write('quit\n')
        os.waitpid(pipe.pid,0)
        return

    def plot_high_res_fit(self):
        #subprocess.call("gnuplot -p high_res.gnuplot > high_res.fit", shell=True)
        pipe = subprocess.Popen('gnuplot -p',shell=True,stdin=subprocess.PIPE)
        pipe.stdin.write("set datafile separator \',\'\n")
        pipe.stdin.write("f(x) = m*x + b\n")
        pipe.stdin.write("set fit logfile \'burn_high_res_trunc_{}.fit\'\n".format(self.data_type))
        pipe.stdin.write("fit f(x) \'burn_test_high_res_trunc.csv\' using 1:(log(${})) via m,b\n".format(self.data_type_int+1))
        pipe.stdin.write("set xlabel \'Frame No.\'\n")
        pipe.stdin.write("set ylabel \'LOG({})\'\n".format(self.data_type))
        pipe.stdin.write("set output \'high_res_trunc_fit_{}.png\'\n".format(self.data_type))
        pipe.stdin.write("plot \'burn_test_high_res_trunc.csv\' using 1:(log(${})), f(x)\n".format(self.data_type_int+1))
        pipe.stdin.write("plot \'burn_test_high_res_trunc.csv\' using 1:(log(${})), f(x)\n".format(self.data_type_int+1))
        pipe.stdin.write('quit\n')
        os.waitpid(pipe.pid,0)
        return

def trim_high_res():
    f = open('burn_test_high_res.csv','r')
    g = open('burn_test_high_res_trunc.csv','w')
    i = 1
    for line in f:
        if i > 1:
            brag_spots_no_ice = int(line.split(', ')[2])
            #print(brag_spots_no_ice)
                
            if brag_spots_no_ice < 2:
                break

        g.writelines(line)
        i = i + 1
        #print(i)

    f.close()
    g.close()
                                   
    return

def get_half_intensity_frame_no(csv_filename):

	half_intensity_frame_no = get_frame_no_at_fraction(csv_filename, 0.5, 6)

	return half_intensity_frame_no

def get_half_spot_frame_no(csv_filename):

	half_spot_frame_no = get_frame_no_at_fraction(csv_filename, 0.5, 1)

	return half_spot_frame_no

def get_half_spot_no_ice_frame_no(csv_filename):

	half_spot_no_ice_frame_no = get_frame_no_at_fraction(csv_filename, 0.5, 2) 

	return half_spot_no_ice_frame_no

#assumes frame no is first column
#input csv filename string and float fraction
#e.g. for half-dose fraction = 0.5

def get_frame_no_at_fraction(csv_filename, fraction, n):
	
	np_array = numpy.genfromtxt(csv_filename, delimiter=',', skiprows=1)
	max_value = get_column_max(np_array,n)
	atten_max_value = fraction*max_value
	for k in range(0,len(np_array[:,n])):
		check = np_array[:,n][k]
		if check < atten_max_value:
			frame_no_index = k
			break	

	return np_array[:,0][frame_no_index]

# input is numpy array and column index int

def get_column_max(np_array, n):

	return np_array[:,n].max()

def run_find_spots_all_res():
	command = "/usr/local/crys-local/phenix-1.17.1-3660/build/bin/dials.find_spots_client"
	subprocess.call(command + " $PWD/../*2.cbf > burn_test_all_res.log", shell=True)
	subprocess.call("$PWD/../passxmltocsv.bash burn_test_all_res.log > burn_test_all_res.csv", shell=True)
	return

def get_d_min():
	i = 1
	f = open('burn_test_all_res.csv','r')
	for line in f:
		if i == 2:
			print(line.split(", "))
			d_min = float(line.split(", ")[5])
			break
		i = i + 1
	f.close()
	
	return d_min
