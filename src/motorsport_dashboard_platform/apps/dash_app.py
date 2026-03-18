from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from time import sleep, time

from ..example_project import EXAMPLE_PROJECT, create_example_project
from ..models import DashboardProject, ProfileDefinition
from ..runtime.rules import AlertEngine
from ..runtime.signals import SignalStore


@dataclass(slots=True)
class DashSnapshot:
    profile_id: str
    page_name: str
    rpm: object
    gear: object
    speed: object
    battery_voltage: object
    can_health: object
    active_alerts: list[str]


class MockTelemetryFeed:
    def __init__(self) -> None:
        self.tick = 0
        self.gears = ["N", "1", "2", "3", "4", "5", "6"]

    def step(self, store: SignalStore) -> None:
        self.tick += 1
        now = time()
        rpm = int(2500 + 6500 * (0.5 + 0.5 * math.sin(self.tick / 4)))
        speed = round(40 + 180 * (0.5 + 0.5 * math.sin(self.tick / 6)), 1)
        gear = self.gears[min(len(self.gears) - 1, max(0, rpm // 1500))]
        battery = round(320 - (self.tick % 40) * 1.5, 1)
        can_health = "timeout" if self.tick % 17 == 0 else "ok"

        store.update("vehicle.engine.rpm", rpm, timestamp=now)
        store.update("vehicle.transmission.gear", gear, timestamp=now)
        store.update("vehicle.speed", speed, timestamp=now)
        store.update("vehicle.battery.voltage", battery, timestamp=now)
        store.update("system.can.bus0.health", can_health, timestamp=now)


class DashController:
    def __init__(self, project: DashboardProject | None = None, *, profile_id: str | None = None):
        self.project = project or create_example_project()
        self.profile = self._resolve_profile(profile_id)
        self.signal_store = SignalStore(self.project)
        self.alert_engine = AlertEngine(self.project)
        self.feed = MockTelemetryFeed()
        self.current_page_index = 0

    def _resolve_profile(self, profile_id: str | None) -> ProfileDefinition:
        if profile_id is None:
            return self.project.profiles[0]
        for profile in self.project.profiles:
            if profile.id == profile_id:
                return profile
        raise KeyError(f"Unknown profile id: {profile_id}")

    def current_page_name(self) -> str:
        page_id = self.profile.page_ids[self.current_page_index]
        for page in self.project.pages:
            if page.id == page_id:
                return page.name
        return page_id

    def next_page(self) -> None:
        self.current_page_index = (self.current_page_index + 1) % len(self.profile.page_ids)

    def tick(self) -> DashSnapshot:
        self.feed.step(self.signal_store)
        active_alerts = [state.alert_id for state in self.alert_engine.evaluate(self.signal_store) if state.active]
        return DashSnapshot(
            profile_id=self.profile.id,
            page_name=self.current_page_name(),
            rpm=self.signal_store.get("vehicle.engine.rpm").value,
            gear=self.signal_store.get("vehicle.transmission.gear").value,
            speed=self.signal_store.get("vehicle.speed").value,
            battery_voltage=self.signal_store.get("vehicle.battery.voltage").value,
            can_health=self.signal_store.get("system.can.bus0.health").value,
            active_alerts=active_alerts,
        )


class DashApplication:
    def __init__(self, controller: DashController | None = None):
        self.controller = controller or DashController(EXAMPLE_PROJECT)

    def run(self) -> None:
        import tkinter as tk
        from tkinter import ttk

        root = tk.Tk()
        root.title("MLSW Dash")
        root.geometry("900x520")
        root.configure(bg="#05070A")

        top = ttk.Frame(root, padding=12)
        top.pack(fill="x")
        body = ttk.Frame(root, padding=12)
        body.pack(fill="both", expand=True)
        footer = ttk.Frame(root, padding=12)
        footer.pack(fill="x")

        page_var = tk.StringVar()
        gear_var = tk.StringVar()
        speed_var = tk.StringVar()
        rpm_var = tk.StringVar()
        battery_var = tk.StringVar()
        can_var = tk.StringVar()
        alerts_var = tk.StringVar()

        ttk.Label(top, textvariable=page_var, font=("Arial", 20, "bold")).pack(anchor="w")
        ttk.Label(top, text=f"Profile: {self.controller.profile.name}").pack(anchor="w")

        ttk.Label(body, text="GEAR", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(body, textvariable=gear_var, font=("Arial", 48, "bold")).grid(row=1, column=0, sticky="w", padx=8, pady=8)

        ttk.Label(body, text="SPEED", font=("Arial", 14, "bold")).grid(row=0, column=1, sticky="w")
        ttk.Label(body, textvariable=speed_var, font=("Arial", 36, "bold")).grid(row=1, column=1, sticky="w", padx=8, pady=8)

        ttk.Label(body, text="RPM", font=("Arial", 14, "bold")).grid(row=2, column=0, sticky="w")
        ttk.Label(body, textvariable=rpm_var, font=("Arial", 32, "bold")).grid(row=3, column=0, sticky="w", padx=8, pady=8)

        ttk.Label(body, text="PACK V", font=("Arial", 14, "bold")).grid(row=2, column=1, sticky="w")
        ttk.Label(body, textvariable=battery_var, font=("Arial", 28, "bold")).grid(row=3, column=1, sticky="w", padx=8, pady=8)

        ttk.Label(body, text="CAN HEALTH", font=("Arial", 14, "bold")).grid(row=4, column=0, sticky="w")
        ttk.Label(body, textvariable=can_var, font=("Arial", 24, "bold")).grid(row=5, column=0, sticky="w", padx=8, pady=8)

        ttk.Label(body, text="ACTIVE ALERTS", font=("Arial", 14, "bold")).grid(row=4, column=1, sticky="w")
        ttk.Label(body, textvariable=alerts_var, font=("Arial", 18, "bold"), foreground="#EB5757").grid(row=5, column=1, sticky="w", padx=8, pady=8)

        def render() -> None:
            snapshot = self.controller.tick()
            page_var.set(snapshot.page_name)
            gear_var.set(str(snapshot.gear))
            speed_var.set(f"{snapshot.speed} km/h")
            rpm_var.set(str(snapshot.rpm))
            battery_var.set(f"{snapshot.battery_voltage} V")
            can_var.set(str(snapshot.can_health).upper())
            alerts_var.set(", ".join(snapshot.active_alerts) if snapshot.active_alerts else "none")
            root.after(250, render)

        ttk.Button(footer, text="Next Page", command=self.controller.next_page).pack(side="left")
        ttk.Button(footer, text="Refresh Now", command=render).pack(side="left", padx=8)

        render()
        root.mainloop()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mlsw-dash", description="Run the MLSW dash application")
    parser.add_argument("--profile", help="Profile id to render", default=None)
    parser.add_argument("--headless", action="store_true", help="Run without a GUI and print snapshots")
    parser.add_argument("--ticks", type=int, default=5, help="Number of mock ticks to emit in headless mode")
    parser.add_argument("--interval", type=float, default=0.05, help="Delay between headless ticks in seconds")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    controller = DashController(EXAMPLE_PROJECT, profile_id=args.profile)

    if args.headless:
        for _ in range(args.ticks):
            snapshot = controller.tick()
            print(
                f"profile={snapshot.profile_id} page={snapshot.page_name} gear={snapshot.gear} "
                f"speed={snapshot.speed} rpm={snapshot.rpm} battery={snapshot.battery_voltage} "
                f"can={snapshot.can_health} alerts={','.join(snapshot.active_alerts) or 'none'}"
            )
            sleep(args.interval)
        return 0

    DashApplication(controller).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
