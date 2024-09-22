import gym
from gym import spaces
import numpy as np
import pandas as pd
from typing import List, Set
from dataclasses import dataclass, field
from tools.df_merges import get_technician_and_device_data


@dataclass
class Technician:
    id: int
    name: str
    rbh_do_zaplanowania: float
    rbh_przydzielone: float
    iums: Set[str]

    def has_ium(self, ium: str) -> bool:
        return ium in self.iums


@dataclass
class Device:
    index: int
    ium: str
    nazwa: str
    typ: str
    nr_fabryczny: str
    rbh_norma: float
    dni_w_om: float
    uzytkownik: str
    technician: Technician | None = field(default=None)


def generate_technicians(technicians: pd.DataFrame) -> List[Technician]:
    technician_list = [Technician(index, row['technician'], row['rbh_do_zaplanowania'], row['rbh_przydzielone'], set(row['iums']))
                       for index, row in technicians.iterrows()]
    return technician_list


def generate_devices(devices: pd.DataFrame) -> List[Device]:
    device_list = [Device(index, str(row['ium']).zfill(6), row['nazwa'], row['typ'], row['nr_fabryczny'], row['rbh_norma'], row['dni_w_om'], row['uzytkownik'])
                   for index, row in devices.iterrows()]
    return device_list


class JobSchedulingEnv(gym.Env):
    def __init__(self, technicians: List[Technician], devices: List[Device]):
        super(JobSchedulingEnv, self).__init__()
        self.technicians = technicians
        self.devices = devices
        self.current_device_index = 0

        self.action_space = spaces.Discrete(len(self.technicians) + 1)  # +1 dla "None"
        self.observation_space = spaces.Box(
            low=0, high=100, shape=(len(devices) + len(technicians),), dtype=np.float32)

        self.hard_constraint_broken = False
        self.soft_constraints_score = 0
        self.state = self._get_observation()

    def _get_observation(self):
        device_features = [device.rbh_norma for device in self.devices]
        technician_features = [technician.rbh_do_zaplanowania for technician in self.technicians]
        return np.array(device_features + technician_features)

    def reset(self):
        self.current_device_index = 0
        self.hard_constraint_broken = False
        self.soft_constraints_score = 0
        self.state = self._get_observation()

        for device in self.devices:
            device.technician = None

        return self.state

    def step(self, action):
        device = self.devices[self.current_device_index]
        reward = -1  # Mała stała kara za każdy krok, aby motywować agenta do działania
        done = False

        if action < len(self.technicians):
            technician = self.technicians[action]
            if technician.has_ium(device.ium) and technician.rbh_do_zaplanowania >= device.rbh_norma:
                # Przypisz technika do urządzenia, jeśli spełnia warunki
                device.technician = technician
                technician.rbh_do_zaplanowania -= device.rbh_norma
                reward += 50  # Duża nagroda za poprawne przypisanie
                print(f"Technician {technician.name} assigned to Device {device.nazwa}. Reward: {reward}")
            else:
                print(f"Failed to assign Technician {technician.name} to Device {device.nazwa} (IUM or RBH mismatch)")
        else:
            # Brak przypisania technika (bez dodatkowej kary)
            device.technician = None
            print(f"No Technician assigned to Device {device.nazwa}")

        # Przechodzenie do kolejnego urządzenia
        self.current_device_index += 1
        if self.current_device_index >= len(self.devices):
            done = True  # Koniec epizodu po przypisaniu wszystkich urządzeń

        # Aktualizacja stanu
        self.state = self._get_observation()

        return self.state, reward, done, {}



    def render(self, mode='human'):
        print(f"Device {self.current_device_index}/{len(self.devices)}")
        print(f"Soft score: {self.soft_constraints_score}")
        if self.hard_constraint_broken:
            print("Hard constraint broken!")


def print_solution(technicians: List[Technician], devices: List[Device], save_to_excel: bool = False, excel_file: str = "rl_device_schedule.xlsx"):
    """
    Wyświetla wynik przypisania techników do urządzeń i zapisuje wynik do pliku Excel.
    """
    devices_data = []
    summary = {}

    for device in devices:
        technician = device.technician
        technician_info = technician.name if technician else "None"
        print(f"Device(index={device.index}, ium={device.ium}, nazwa={device.nazwa}, typ={device.typ}, "
              f"assigned_technician={technician_info}, rbh_norma={device.rbh_norma})")

        devices_data.append({
            "Device Index": device.index,
            "Days in OM": device.dni_w_om,
            "IUM": device.ium,
            "Device Name": device.nazwa,
            "Device Type": device.typ,
            "Serial Number": device.nr_fabryczny,
            "RBH Norma": device.rbh_norma,
            "User": device.uzytkownik,
            "Technician": technician_info
        })

        if technician:
            if technician.id not in summary:
                summary[technician.id] = {'name': technician.name, 'total_norma_rbh': 0, 'rbh_do_zaplanowania': technician.rbh_do_zaplanowania}
            summary[technician.id]['total_norma_rbh'] += device.rbh_norma

    # Sprawdzanie przypisań dla każdego technika
    for technician_id, technician_info in summary.items():
        total_rbh = technician_info['total_norma_rbh']
        rbh_do_zaplanowania = technician_info['rbh_do_zaplanowania']
        if total_rbh > rbh_do_zaplanowania:
            print(f"[ERROR] Technician(id={technician_id}, name={technician_info['name']}) "
                  f"total norma_rbh: {total_rbh} exceeds available hours: {rbh_do_zaplanowania}")
        else:
            print(f"Technician(id={technician_id}, name={technician_info['name']}) "
                  f"total norma_rbh: {total_rbh}, rbh_do_zaplanowania: {rbh_do_zaplanowania}")

    if save_to_excel:
        df = pd.DataFrame(devices_data)
        df_sorted = df.sort_values(by='Days in OM', ascending=False)

        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df_sorted.to_excel(writer, index=False, sheet_name='Device Schedule')
            worksheet = writer.sheets['Device Schedule']
            worksheet.autofilter(0, 0, df_sorted.shape[0], df_sorted.shape[1] - 1)

        print(f"\nSolution saved to {excel_file}")


if __name__ == '__main__':
    from stable_baselines3 import PPO

    technicians_df, devices_in_bok_to_assign = get_technician_and_device_data(use_archive_data=False)

    technicians_list = generate_technicians(technicians_df)
    devices_list = generate_devices(devices_in_bok_to_assign)

    env = JobSchedulingEnv(technicians_list, devices_list)
    from stable_baselines3.common.policies import ActorCriticPolicy

    policy_kwargs = dict(
        net_arch=[512, 512],  # Zwiększenie liczby neuronów w sieci neuronowej
    )

    model = PPO("MlpPolicy", env, verbose=1, policy_kwargs=policy_kwargs, learning_rate=1e-4, gamma=0.99, ent_coef=0.01)


    # Trening modelu RL
    model.learn(total_timesteps=10000)

    # Wyświetlanie i zapisywanie rozwiązania po treningu
    print_solution(technicians_list, devices_list, save_to_excel=True)
