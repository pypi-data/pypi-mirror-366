from typing import List, Tuple

import numpy as np

from cratonapi.datacontainers import (Cube, CubeDataSlice, Curve, Grid,
                                      GridDisplayProperties, TransformMatrix,
                                      WellCurve, WellHodograph, WellTrajectory)
from cratonapi.ioconnections import IOBase
from cratonapi.parsers.dataparsers import *
from cratonapi.parsers.dataparsers import cubesaroundpointparser
from cratonapi.requests.datarequests import *
from cratonapi.requests.datarequests import (cubesaroundpointrequest,
                                             uploadwellhodographrequest)
from cratonapi.requests.utilityrequests import dataconnectorgreetingrequest

NUMBER_OF_BYTES_FOR_ONE_TRACE_VALUE = 4
MAXIMUM_CUBE_BATCH_BYTE_SIZE = int(1024**2 * 500)


class DataConnector:
    connection: IOBase
    app_id: int

    def __init__(self, connection: IOBase, new_app_id: int = 1):
        self.connection = connection
        self.app_id = new_app_id
        # self.__greeting()

    def __greeting(self) -> None:
        message = dataconnectorgreetingrequest.request(self.app_id)
        self.connection.write(message)

    def upload_grid(self, name: str, grid: Grid) -> None:
        """Download code 1"""
        message = uploadgridrequest.request(name, grid)
        self.connection.write(message)

    def upload_well_hodograph(self, well_id: int, hodograph: WellHodograph) -> None:
        """Download code 6"""
        message = uploadwellhodographrequest.request(well_id, hodograph)
        self.connection.write(message)

    def upload_well_curves(self, well_curve: WellCurve, well_id: int) -> None:
        """Download code 2"""
        message = uploadwellcurvesrequest.request(well_curve, well_id)
        self.connection.write(message)

    def get_wells_list(self) -> np.ndarray:
        """Request code 1"""
        message = welllistrequest.request()
        self.connection.write(message)
        answer = self.connection.read()
        return welllistparser.parse(answer)

    def get_wells_data(self, count: int = 0, *wells_ids: int) -> np.ndarray:
        """Request code 2"""
        message = wellsrequest.request(count, *wells_ids)
        self.connection.write(message)
        answer = self.connection.read()
        return wellsparser.parse(answer)

    def get_well_curves(self, well_id: int) -> List[WellCurve]:
        """Request code 3"""
        message = wellcurvesrequest.request(well_id)
        self.connection.write(message)
        answer = self.connection.read()
        return wellcurvesparser.parse(answer)

    def get_stratigraphic_levels(self) -> np.ndarray:
        """Request code 4"""
        message = stratigraphiclevellistrequest.request()
        self.connection.write(message)
        answer = self.connection.read()
        return stratigraphiclevelsparser.parse(answer)

    def get_well_stratigraphic_levels(self, well_id: int) -> np.ndarray:
        """Request code 5"""
        message = wellstratigraphiclevellistrequest.request(well_id)
        self.connection.write(message)
        answer = self.connection.read()
        return wellstratigraphiclevelsparser.parse(answer)

    def get_grids_list(self) -> np.ndarray:
        """Request code 6"""
        message = gridlistrequest.request()
        self.connection.write(message)
        answer = self.connection.read()
        return gridlistparser.parse(answer)

    def get_grid(self, grid_id: int) -> Grid:
        """Request code 7"""
        message = gridrequest.request(grid_id)
        self.connection.write(message)
        answer = self.connection.read()
        return gridparser.parse(answer)

    def get_well_hodograph(self, well_id: int) -> WellHodograph:
        """Request code 8"""
        message = wellhodographrequest.request(well_id)
        self.connection.write(message)
        answer = self.connection.read()
        return wellhodographparser.parse(answer)

    def get_well_trajectory(self, well_id: int) -> WellTrajectory:
        """Request code 9"""
        message = welltrajectoryrequest.request(well_id)
        self.connection.write(message)
        answer = self.connection.read()
        return welltrajectoryparser.parse(answer)

    def get_grid_display_properties(self, grid_id: int) -> GridDisplayProperties:
        """Request code 10"""
        message = griddisplaypropertiesrequest.request(grid_id)
        self.connection.write(message)
        answer = self.connection.read()
        return griddisplaypropertiesparser.parse(answer)

    def get_curve_display_properties(self) -> np.ndarray:
        """Request code 12"""
        message = curvedisplaypropertiesrequest.request()
        self.connection.write(message)
        answer = self.connection.read()
        return curvedisplaypropertiesparser.parse(answer)

    def get_grid_sp(self, grid_id: int) -> np.ndarray:
        """Request code 16"""
        message = gridsprequest.request(grid_id)
        self.connection.write(message)
        answer = self.connection.read()
        return gridspparser.parse(answer)

    def get_cubes(self) -> np.ndarray:
        """Request code 17"""
        message = cubesrequest.request()
        self.connection.write(message)
        answer = self.connection.read()
        return cubesparser.parse(answer)

    def get_cube_horizons(self, cube_id: int) -> np.ndarray:
        """Request code 18"""
        message = cubehorizonsrequest.request(cube_id)
        self.connection.write(message)
        answer = self.connection.read()
        return cubehorizonsparser.parse(answer)

    def _get_cube_data_range_batch(
        self,
        cube_id: int,
        horizon_top_name: str,
        horizon_bot_name: str,
        top_off: float,
        bot_off: float,
        start_inline_idx: int,
        end_inline_idx: int,
        start_crossline_idx: int,
        end_crossline_idx: int,
    ) -> CubeDataSlice:
        message = cubedatarangerequest.request(
            cube_id,
            horizon_top_name,
            horizon_bot_name,
            top_off,
            bot_off,
            start_inline_idx,
            end_inline_idx,
            start_crossline_idx,
            end_crossline_idx,
        )
        self.connection.write(message)
        answer = self.connection.read()
        return cubedatarangeparser.parse(answer)

    def get_cube_data_range(
        self,
        cube_id: int,
        horizon_top_name: str,
        horizon_bot_name: str,
        top_off: float,
        bot_off: float,
        start_inline_idx: int,
        end_inline_idx: int,
        start_crossline_idx: int,
        end_crossline_idx: int,
    ) -> CubeDataSlice:
        """Request code 19"""
        # Нужно подумать как правильно оформить процедуру чтения по батчам. Может быть вынести код в отдельный скрипт
        cube_props = self.get_cube_properties(cube_id)
        approximate_number_of_traces = (end_inline_idx - start_inline_idx) * (
            end_crossline_idx - start_crossline_idx
        )
        approximate_samples_count = cube_props.samples_count
        approximate_trace_size = (
            approximate_samples_count * NUMBER_OF_BYTES_FOR_ONE_TRACE_VALUE
        )
        approximate_size = (
            approximate_number_of_traces
            * approximate_samples_count
            * NUMBER_OF_BYTES_FOR_ONE_TRACE_VALUE
        )

        if approximate_size > MAXIMUM_CUBE_BATCH_BYTE_SIZE:
            batch_inline_size = MAXIMUM_CUBE_BATCH_BYTE_SIZE // (
                approximate_trace_size * (end_crossline_idx - start_crossline_idx)
            )

            cubes_list = []
            for i in range(start_inline_idx, end_inline_idx, batch_inline_size):
                start = i
                end = min(end_inline_idx, start + batch_inline_size - 1)
                cube_i = self._get_cube_data_range_batch(
                    cube_id=cube_id,
                    horizon_top_name=horizon_top_name,
                    horizon_bot_name=horizon_bot_name,
                    top_off=top_off,
                    bot_off=bot_off,
                    start_inline_idx=start,
                    end_inline_idx=end,
                    start_crossline_idx=start_crossline_idx,
                    end_crossline_idx=end_crossline_idx,
                )
                cubes_list.append(cube_i)

            samples_count = cubes_list[0].samples_count
            start_idx = cubes_list[0].start_idx
            inlines = np.hstack([cubes_list[i].inlines for i in range(len(cubes_list))])
            xlines = np.hstack([cubes_list[i].xlines for i in range(len(cubes_list))])
            # Думаю стотит заменить np.vstack на np.concatenate внутри цикла.
            data = np.vstack(
                [cubes_list[i].data for i in range(len(cubes_list))]
            ).astype("float32")
            cube = CubeDataSlice(
                samples_count=samples_count,
                start_idx=start_idx,
                inlines=inlines,
                xlines=xlines,
                data=data,
            )
            return cube
        else:
            cube = self._get_cube_data_range_batch(
                cube_id=cube_id,
                horizon_top_name=horizon_top_name,
                horizon_bot_name=horizon_bot_name,
                top_off=top_off,
                bot_off=bot_off,
                start_inline_idx=start_inline_idx,
                end_inline_idx=end_inline_idx,
                start_crossline_idx=start_crossline_idx,
                end_crossline_idx=end_crossline_idx,
            )
            return cube

    def get_cube_properties(self, cube_id: int) -> Cube:
        """Request code 20"""
        message = cubepropertiesrequest.request(cube_id)
        self.connection.write(message)
        answer = self.connection.read()
        return cubepropertiesparser.parse(answer)

    def get_cubes_around_point(
        self, x: float, y: float, radius: float
    ) -> Tuple[int, List[int]]:
        """Request code 21"""
        message = cubesaroundpointrequest.request(x=x, y=y, radius=radius)
        self.connection.write(message)
        answer = self.connection.read()
        return cubesaroundpointparser.parse(answer)

    def get_transform_matrix(self, cube_id: int) -> TransformMatrix:
        """Request code 27"""
        message = transformmatrixrequest.request(cube_id)
        self.connection.write(message)
        answer = self.connection.read()
        return transformmatrixparser.parse(answer)

    def get_curves_list(self, well_id: int) -> np.ndarray:
        """Request code 28"""
        message = curvelistrequest.request(well_id)
        self.connection.write(message)
        answer = self.connection.read()
        return curvelistparser.parse(answer)

    def get_well_curve(self, well_id: int, curve_id: int) -> Curve:
        """Request code 29"""
        message = wellcurverequest.request(well_id, curve_id)
        self.connection.write(message)
        answer = self.connection.read()
        return wellcurveparser.parse(answer)

    def get_outlines_list(self) -> np.ndarray:
        """Request code 30"""
        message = outlinelistrequest.request()
        self.connection.write(message)
        answer = self.connection.read()
        return outlinelistparser.parse(answer)

    def get_outline(self, outline_id: int) -> np.ndarray:
        """Request code 31"""
        message = outlinerequest.request(outline_id)
        self.connection.write(message)
        answer = self.connection.read()
        return outlineparser.parse(answer)

    def disconnect(self) -> None:
        self.connection.disconnect()
