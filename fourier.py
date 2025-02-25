from manim import *
from manim.typing import Point3D
import numpy as np
from typing import Callable


def print_mob_bb(mob: Mobject):
    print(f"({mob.get_x(LEFT)},{mob.get_y(UP)}) to ({mob.get_x(RIGHT)},{mob.get_y(DOWN)})")


class FourierFilterScene(Scene):

    def get_whitenoise_function(self) -> Callable[[float], float]:
        return lambda x: 1

    def get_multispike_function(self, spike_times: list[float]) -> Callable[[float], float]:
        return lambda x: sum(
            [(-np.tanh((x - 1) / 8) + 1) * np.exp(-100 * (x - m) ** 2) for m in spike_times]
        )

    def get_filter_graph(
        self, size: float
    ) -> tuple[Axes, VGroup, ParametricFunction, ParametricFunction]:
        ax = Axes(
            x_range=[0, 11, 0.1],
            y_range=[0, 1.2, 0.1],
            x_length=size,
            y_length=size,
            axis_config={
                "include_ticks": False,
                "include_tip": False,
                "tip_shape": StealthTip,
                "length": 4,
            },
            x_axis_config={
                # "scaling": LogBase(2),
            },
        ).set_z_index(10)

        labels = ax.get_axis_labels(x_label="f", y_label="I")
        graph_i = ax.plot(self.get_whitenoise_function()).set_color(BLUE_C)
        graph_f = ax.plot(self.get_multispike_function(list(range(1, 11)))).set_color(BLUE_C)

        return (ax, labels, graph_i, graph_f)


class FourierFilterStandalone(FourierFilterScene):

    def construct(self):
        (ax, labels, graph_i, graph_f) = self.get_filter_graph(7)

        self.add(ax, graph_i, labels)
        self.play(Transform(graph_i, graph_f), play_time=2)


class TubeWave(Scene):

    def wave(
        self,
        grid_container: Mobject,
        container_buff=SMALL_BUFF,
        grid_width=20,
        grid_height=20,
        grid_buf: float | tuple[float, float] = 0.075,
        grid_radius=0.02,
        amplitude=0.4,
        periods=0.5,
        random_strength=0.1,
    ):
        t = ValueTracker(0)
        aux_dots = VGroup(*[Dot(radius=grid_radius) for i in range(grid_width * grid_height)])
        (
            aux_dots.arrange_in_grid(grid_height, grid_width, grid_buf)
            .scale_to_fit_width(grid_container.width * (1 - container_buff))
            .scale_to_fit_height(grid_container.height * (1 - container_buff))
            .center()
        )

        # Parameters
        phase = aux_dots[0].get_x()  # Phase shift
        w = aux_dots[-1].get_x() - phase  # Width of the wave

        dots = []
        for dot in aux_dots:
            x = dot.get_x()
            dot.shift(
                ((np.random.random() - 0.5) * UP + (np.random.random() - 0.5) * RIGHT)
                * random_strength
#                * np.sin(np.pi * (x - phase) / w) ** 2
            )
            x, y, z = dot.get_center()
            dot = always_redraw(
                lambda x=x, y=y, z=z: Dot(
                    [
                        x
                        + amplitude
                        * np.sin(2 * PI * periods / w * (x - phase))
                        * np.cos(-t.get_value()),
                        y,
                        z,
                    ],
                    radius=grid_radius,
                    color=BLUE_D,
                )
            )
            dots.append(dot)

        dots = (
            VGroup(*dots)
            .scale_to_fit_height(grid_container.height * (1 - container_buff))
            .scale_to_fit_width(grid_container.width * (1 - container_buff))
            .center()
        )

        self.add(dots)

        return t

    def construct(self):
        ### Build tube and wave
        # Parameters
        tube_length = 10
        tube_diameter = 3
        tube_inner_buff = 0.1
        grid_resolution = 10
        grid_radius = 0.02
        grid_buf_x = 0.32
        grid_buf_y = 0.3
        periods = 2.5
        amplitude = 0.2
        oscillation_speed = 6
        duration = 1

        tube = Rectangle(width=tube_length, height=tube_diameter).center()

        wave_timer = self.wave(
            tube,
            container_buff=tube_inner_buff,
            grid_width=tube_length * grid_resolution,
            grid_height=tube_diameter * grid_resolution,
            grid_buf=(grid_buf_x, grid_buf_y),
            grid_radius=grid_radius,
            amplitude=amplitude,
            periods=periods,
            random_strength=0.2,
        )

        self.add(tube)
        self.play(
            wave_timer.animate.set_value(PI * duration * oscillation_speed),
            rate_func=linear,
            run_time=PI * duration,
        )
