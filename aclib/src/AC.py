import numpy as np
import pandas as pd
from pathlib import Path
import datetime
from aclib.src.utilities import *

plt.rcParams['font.sans-serif'] = "Arial"
plt.rcParams['font.family'] = "sans-serif"


class AC:
    __version__ = "2021.5.5"
    
    def __init__(self, path:Path, sheet_num:int):
        """

        :param path:
        ..:TODO:    - check if path is instance of Path
        ..:TODO:    - add set_context - talk, poster, paper
        """
        self.sheet_num = sheet_num
        self.path = path
        self.raw_data = read_raw_excel(self.path, sheet=sheet_num)
        self.meta = {"timestamp": datetime.datetime.now(),
                     "project": None}
        self.temperature = get_array_for('Temperature', self.raw_data).astype(np.float)
        self.speed = get_array_for('Speed', self.raw_data).astype(np.float)
        self.time = get_array_for('Time', self.raw_data)
        self.elapsed = get_array_for('Elapsed', self.raw_data).astype(np.float)
        self.profile_num = get_array_for('Position', self.raw_data)
        data_matrix = self.raw_data[self.raw_data.iloc[:, 0].map(type) == float]. \
            dropna().values.astype(np.float)
        self.profiles = data_matrix[:, 1:]
        self.position = data_matrix[:, 0]

    def __str__(self) -> str:
        print(self.meta['Sample'], ' | ', self.meta['Measurement'])
        print('---------------------------------------------------------------')
        print('Data recorded on', self.meta['Record Date'])
        print('{} profiles acquired at an interval of {} secs each'.format(self.profiles.shape[1],
              np.round(np.mean(np.diff(self.elapsed)),2)))
        print('Temperature of experiment was {} degrees'.format(np.round(np.mean(self.temperature)), 2))
        print('Speed of experiment was {} RPM'.format(np.round(np.mean(self.speed)), 2))
        print('Experiment started at {} and stopped at {}'.format(self.time[0], self.time[-1]))

    def _set_project(self, name_of_project):
        """[summary]

        Args:
            name_of_project ([type]): [description]
        """
        self.meta["project"] = name_of_project

    def _extract_meta_from_raw_data(self)-> None:
        """[summary]
        """
        f = ['Sample', 'Measurement', 'Record Date']
        self.meta.update(dict(zip(f, [get_value_for(i, self.raw_data) for i in f])))

    def print_info(self):
        """[summary]
        """
        self.__str__()

    def replace_implausible_transmission_values(self):
        """[summary]
        """
        # TODO: add check for implausible values first
        self.profiles = np.clip(self.profiles, 0.1, 99.99)

    def __eval__(self, replace_implausible=True, verbose=True):
        """[summary]

        Args:
            replace_implausible (bool, optional): [description]. Defaults to True.
            verbose (bool, optional): [description]. Defaults to True.
        """
        self._extract_meta_from_raw_data()
        if replace_implausible:
            self.replace_implausible_transmission_values()
        if verbose:
            self.print_info()

    def show_data_distribution(self, save=False):
        """[summary]

        Args:
            save (bool, optional): [description]. Defaults to False.
        """
        fig_hist, ax_hist = plt.subplots(figsize=(7, 7))
        sns.set_style('white')
        sns.distplot(self.profiles.ravel())
        if save==True:
            fname = self.meta['Sample'] + 'raw_transmission_hist.png'
            plt.savefig(fname, dpi=300, bbox_inches='tight')
        plt.show()

    def plot_transmittogram(self, power=1, tmax=100, color=plt.cm.gray):
        """[summary]
        # :param tmax:
        # :param power:
        # :param color:
        # :return:
        # ...:TODO:   - check crowding of axes
        #             - add quantile based plotting
        #             - select time axis limit
        #             - check if really tmax is needed
        #             - settle on choice of  sns or plt

        Args:
            power (int, optional): [description]. Defaults to 1.
            tmax (int, optional): [description]. Defaults to 100.
            color ([type], optional): [description]. Defaults to plt.cm.gray.
        """
        title = self.meta['Sample'] + ' | ' + self.meta['Measurement']
        y_ticks = np.round(self.position, 0).astype(np.int)
        transmission = pd.DataFrame(self.profiles)
        transmission = transmission.set_index(y_ticks)
        transmission.columns = np.round(self.elapsed/60, 1)
        # 17 values look clean on the figure of size (12, 7) 
        # Converted to list as seaborn wants a list
        xspacing = np.ceil(self.elapsed.shape[0]/17).astype(int).tolist() 
        ax_t = gen_tgram_plot(transmission=transmission, power=power, xspacing=xspacing, color=color)
        ax_t.set_xticklabels(ax_t.get_xticklabels(), rotation=45, 
                   horizontalalignment='right')
        ax_t.set_yticklabels(ax_t.get_yticklabels(), rotation=0, 
                           horizontalalignment='right')
        ax_t.figure.axes[-1].yaxis.label.set_size(22)
        cbar = ax_t.collections[0].colorbar
        cbar.ax.tick_params(labelsize=20)
        ax_t.set_xlabel('Elapsed Time, min', size=22)
        ax_t.set_ylabel('Radial Position, mm', size=22)
        ax_t.set_title(title, size=14, loc='left', pad=25)
        ax_t.tick_params(bottom = True, left = True, 
                       direction = 'out',labelsize=18, width=2)      
        plt.tight_layout()
        # plt.show()

    def time_lapse(self, width=5):
        """[summary]

        Args:
            width (int, optional): [description]. Defaults to 5.
        """
        import matplotlib.animation as animation
        file_name = self.meta['Sample'] + '_time_lapse.gif'
        fig = plt.figure(figsize=(3, 7))
        ims = []
        N = self.profile_num.shape[0] // width
        for i in range(N):
            # im = plt.imshow(y.iloc[:, :j], extent=(-0.5, 3.5, -0.5, 9.5))
            im = plt.imshow(self.profiles[:, width * i:width * (i + 1)], extent=(-0.5, 3.5, -0.5, 9.5),
                            cmap=plt.cm.gray)
            ims.append([im])

        ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat_delay=1000)

        ani.save(file_name)
        
    def plot_profiles(self, skip=None):
        """[summary]

        Args:
            skip ([type], optional): [description]. Defaults to None.
        """
        # TODO: - add choice of gradient color
        title = self.meta['Sample'] + ' | ' + self.meta['Measurement']
        fig, ax = plt.subplots(figsize=(8,6))
        colors = plt.cm.viridis(np.linspace(0,1,self.profile_num.shape[0]))
        if skip is None:
            for profile in range(self.profile_num.shape[0]):
                    ax.plot(self.position, self.profiles[:, profile], color=colors[profile])
        else:
            profile_indices = np.arange(0, self.profile_num.shape[0], skip)
            for profile in profile_indices:
                    ax.plot(self.position, self.profiles[:, profile], color=colors[profile])            
        ax.set_ylabel('Transmission, %', size=22)
        ax.set_xlabel('Position, mm', size=22)
        ax.set_title(title, size=10, loc='left', pad=25)
        ax.set_ylim(0,100)
        plt.xlim(self.position[0], self.position[-1])
        ax.tick_params(axis='both', labelsize=18)
        plt.tight_layout()
        plt.show()