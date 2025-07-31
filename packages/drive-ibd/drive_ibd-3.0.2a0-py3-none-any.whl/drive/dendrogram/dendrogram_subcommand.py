from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy.typing as npt
import pandas as pd
import scipy.cluster.hierarchy as sch
from log import CustomLogger
from numpy import zeros
from scipy.spatial.distance import squareform

from drive.network.filters import IbdFilter
from drive.network.models import create_indices
from drive.utilities.functions import split_target_string

logger = CustomLogger.get_logger(__name__)


class NetworkIDNotFound(Exception):
    def __init__(self, network_id: str) -> None:
        self.msg = f"The id, {network_id}, was not found in the IBD data. Make sure that the ID you are looking for perfectly matches what should be in the DRIVE file. Trailing zeros can make a difference, 10.0 != 10 in DRIVE."
        super().__init__(self.msg)


def check_kwargs(args_dict: dict[str, Any]) -> Optional[str]:
    """Function that will make sure that the necessary arguments are passed to distance function

    Parameters
    ----------
    args_dict : Dict[str, Any]
        Dictionary that has the arguments as keys and the values for the distance function
    """
    if not all(
        [
            elem in args_dict.keys()
            for elem in ["pair_1", "pair_2", "pairs_df", "cm_threshold"]
        ]
    ):
        return "Not enough arguments passed to the _determine_distances function. \
            Expected pair_1, pair_2, pairs_df, cm_threshold"


def _determine_distances(**kwargs) -> tuple[Optional[str], float]:
    """Function that will determine the distances between the main grid and then \
        each connected grid. It will use a value of 2.5 for all grids that don't \
            share a segment. This is just the min cM value, 5cM, divided in half

    Parameters
    ----------
    pair_1 : str
        string that has the main grid id


    pairs_df : pd.DataFrame
        dataframe from the pairs file that has been filtered to just connections \
            with the main grid
    """
    # checking to make sure the function has the right parameters in the kwargs and then
    # returning an error if it doesn't
    err = check_kwargs(kwargs)

    if err != None:
        return err, 0.0

    # getting all the necessary values out of the kwargs dict
    pair_1 = kwargs.pop("pair_1")
    pair_2 = kwargs.pop("pair_2")
    pairs_df = kwargs.pop("pairs_df")
    min_cM = kwargs.pop("cm_threshold")

    if pair_2 == pair_1:
        return None, float(0)

    # pulling out the length of the IBD segment based on hapibd
    filtered_pairs: pd.DataFrame = pairs_df[
        ((pairs_df["pair_1"] == pair_1) & (pairs_df["pair_2"] == pair_2))
        | ((pairs_df["pair_1"] == pair_2) & (pairs_df["pair_2"] == pair_1))
    ]

    if filtered_pairs.empty:
        ibd_length: float = min_cM / 2

        # print(
        #     f"no pairwise sharing for grids {pair_1} and {pair_2}. Using an ibd length of {ibd_length}cM instead"
        # )

    else:
        ibd_length: float = filtered_pairs.iloc[0]["length"]

    return None, 1 / ibd_length


def record_matrix(output: Union[Path, str], matrix, pair_list: List[str]) -> None:
    """Function that will write the distance matrix to a file

    Parameters
    ----------
    output : str
        filepath to write the output to

    matrix : array
        array that has the distance matrix for each individual

    pair_list : List[str]
        list of ids that represent each row of the pair_list
    """

    with open(output, "w") as output_file:
        for i in range(len(pair_list)):
            distance_str = "\t".join([str(distance) for distance in matrix[i]])
            output_file.write(f"{pair_list[i]}\t{distance_str}\n")


def make_distance_matrix(
    pairs_df: pd.DataFrame,
    min_cM: int,
    distance_function: Callable = _determine_distances,
) -> tuple[Union[List[str], None], npt.NDArray]:
    """Function that will make the distance matrix

    Parameters
    ----------
    pairs_df : pd.DataFrame
        dataframe that has the pairs_files. it should have at least three columns
        called 'pair_1', 'pair_2', and 'length'

    min_cM : float
        This is the minimum centimorgan threshold that will be divided in half to
        get the ibd segment length when pairs do not share a segment

    Returns
    -------
    Dict[str, Dict[str, float]]
        returns a tuple where the first object is a list of ids that has the
        individual id that corresponds to each row. The second object is the
        distance matrix
    """
    # get a list of all the unique ids in the pairs_df
    id_list = list(
        set(pairs_df.pair_1.values.tolist() + pairs_df.pair_2.values.tolist())
    )

    matrix = zeros((len(id_list), len(id_list)), dtype=float)

    ids_index = []

    for i in range(len(id_list)):
        ids_index.append(id_list[i])

        for j in range(len(id_list)):
            err, distance = distance_function(
                pair_1=id_list[i],
                pair_2=id_list[j],
                pairs_df=pairs_df,
                cm_threshold=min_cM,
            )
            if err != None:
                print(err)
                return None, None

            matrix[i][j] = distance

    return ids_index, matrix


def generate_dendrogram(matrix: npt.NDArray) -> npt.NDArray:
    """Function that will perform the hierarchical clustering algorithm

    Parameters
    ----------
    matrix : Array
        distance matrix represented by 2D numpy array.
        distance should be calculated based on 1/(ibd segment
        length)

    Returns
    -------
    Array
        returns the results of the clustering as a numpy array
    """
    squareform_matrix = squareform(matrix)

    return sch.linkage(squareform_matrix, method="ward")


# def _check_for_overlap(cases: List[str], exclusions: List[str]) -> None:
#     """Make sure there is no overlap between individuals in the cases and exclusions \
#         list provided to the _generate_label_colors method

#     Parameters
#     ----------
#     cases : List[str]
#         list of individuals who are considered cases for a
#         disease or phenotype

#     exclusions : List[str]
#         list of individuals who are consider exclusions and are indicated as N/A or
#         -1 by the phenotype file. This value defaults to None.

#     Raises
#     ------
#     ValueError
#         If there are overlapping individuals in the cases and exclusions lists then a \
#             ValueError is raised to indicate that the user should check their labelling.
#     """
#     if [ind for ind in cases if ind in exclusions]:
#         raise ValueError(
#             "Overlapping individuals found between cases and exclusions \
#                         lists. Please check your case and exclusions list labelling."
#         )


# def _generate_label_colors(
#     grid_list: List[str], cases: List[str], exclusions: List[str] = []
# ) -> Dict[str, str]:
#     """Function that will generate the color dictionary
#     indicating what color each id label should be

#     Parameters
#     ----------
#     grid_list : list[str]
#         list of id strings

#     cases : List[str]
#         list of individuals who are considered cases for a
#         disease or phenotype

#     exclusions : List[str]
#         list of individuals who are consider exclusions and are indicated as N/A or
#         -1 by the phenotype file. This value defaults to None

#     Returns
#     -------
#     dict[str,str]
#         returns a dictionary where the key is the id and the
#         values are the color of the label for that id.
#     """

#     if exclusions:
#         _check_for_overlap(cases, exclusions)

#     color_dict = {}

#     for grid in grid_list:
#         if grid in cases:
#             color_dict[grid] = "r"
#         elif grid in exclusions:
#             color_dict[grid] = "g"
#         else:
#             color_dict[grid] = "k"

#     return color_dict


def draw_dendrogram(
    clustering_results: npt.NDArray,
    grids: List[str],
    output_name: Union[Path, str],
    # cases: Optional[List[str]] = None,
    # exclusions: List[str] = [],
    title: Optional[str] = None,
    node_font_size: int = 10,
) -> tuple[plt.Figure, plt.Axes, Dict[str, Any]]:
    """Function that will draw the dendrogram

    Parameters
    ----------
    clustering_results : npt.NDArray
        numpy array that has the results from running the generate_dendrogram function

    grids : list[str]
        list of ids to use as labels

    output_name : Path | str
        path object or a string that tells where the
        dendrogram will be saved to.

    # cases : list[str] | None
    #     list of case ids. If the user doesn't provided this
    #     value then all of the labels on the dendrogram will
    #     be black. If the user provides a value then the case
    #     labels will be red. Value defaults to None

    # exclusions : List[str]
    #     list of individuals who are consider exclusions and are
    #     indicated as N/A or -1 by the phenotype file. This value
    #     defaults to None

    title : str | None
        Optional title for the plot. If this is not provided
        then the plot will have no title

    node_font_size : int
        Size for the font of the dendrogram leaf nodes

    Returns
    -------
    tuple[plt.Figure, plt.Axes, dict[str, Any]]
        returns a tuple with the matplotlib Figure, the
        matplotlib Axes object, and a dictionary from the sch.
        dendrogram command
    """
    figure = plt.figure(figsize=(15, 12))
    ax = plt.subplot(111)

    # Temporarily override the default line width:
    with plt.rc_context(
        {
            "lines.linewidth": 2,
        }
    ):
        dendrogram = sch.dendrogram(
            clustering_results,
            labels=grids,
            orientation="left",
            color_threshold=0,
            above_threshold_color="black",
            leaf_font_size=node_font_size,
        )

    # change the color of the nodes for cases if the user wants to.

    # # remove whitespace from the case labels
    # cases = [case.strip() for case in cases]

    # if cases:
    #     color_dict = _generate_label_colors(grids, cases, exclusions)
    #     yaxis_labels = ax.get_ymajorticklabels()
    #     for label in yaxis_labels:
    #         label.set_color(color_dict[label.get_text()])

    # removing the ticks and axes
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.axes.get_xaxis().set_visible(False)

    if title:
        plt.title(title, fontsize=20)

    plt.savefig(output_name)

    return figure, ax, dendrogram


def load_networks(
    drive_results: Path,
    max_network_size: int,
    min_network_size: int,
    network_id: str = Optional[str],
) -> dict[str, List[str]]:
    """method reads the drive networks into a dictionary. If the user chooses to
    generate dendrograms for all the networks then DRIVe only returns those
    networks that are between a certain size range

    Parameters
    ----------
    drive_results : Path
        output file from running the clustering step of DRIVE

    max_network_size : int
        the maximum size of a network that will be allowed in the analysis.
        Drawing large networks well is hard to automate. The default value is 30

    min_network_size : int
        minimum size of a network to draw. Drawing 2 person networks makes no
        sense so by default DRIVE only draws dendrograms for networks of 3 or
        more people. Users can choose a different value if they wish.

    network_id : str
        the id of the cluster ID by DRIVE. Default value = none

    Returns
    -------
    dict[str, list[str]]
        returns a dictionary where the keys are the cluster IDs and the values
        are a list of haplotypes in the cluster

    Raises
    ------
    NetworkIDNotFount
        raises a KeyError if the network_id value is not found in the drive file
    """
    return_dict = {}

    with open(drive_results, "r", encoding="utf-8") as drive_file:
        logger.verbose(
            f"Identifying network {network_id} within the DRIVE output, {drive_results}"
        )
        if network_id:
            for line in drive_file:
                (
                    clst_id,
                    network_size,
                    haplotype_count,
                    edge_count,
                    connectedness,
                    _,
                    id_list,
                    haplotype_list,
                    *_,
                ) = line.strip().split("\t")
                if clst_id == network_id:
                    return_dict[clst_id] = {
                        "ids": id_list.strip().split(","),
                        "haplotypes": haplotype_list.strip().split(","),
                    }

            if not return_dict:
                logger.critical(
                    f"The id {network_id} was not found within the DRIVE file at {drive_file}."
                )
                raise NetworkIDNotFound(network_id)
        else:
            logger.verbose(
                "No network id passed to program. Reading in data for all of the networks identified by DRIVE."
            )
            logger.verbose(
                f"For the sake of drawing efficiency, only gathering dendrograms that are between size {min_network_size} and {max_network_size}"
            )

            for line in drive_file:
                # we can skip the header line
                if "clstID" in line:
                    pass
                else:
                    (
                        clst_id,
                        network_size,
                        haplotype_count,
                        edge_count,
                        connectedness,
                        _,
                        id_list,
                        haplotype_list,
                        *_,
                    ) = line.strip().split("\t")
                    if min_network_size <= len(id_list.split(",")) <= max_network_size:
                        return_dict[clst_id] = {
                            "ids": id_list.strip().split(","),
                            "haplotypes": haplotype_list.strip().split(","),
                        }

    logger.debug(f"Stored {len(return_dict.keys())} networks within the dictionary")

    return return_dict


def generate_dendrograms(args) -> None:
    # need to add read in the drive networks to get the appropriate ids
    network_ids = load_networks(
        args.input, args.max_network_size, args.min_network_size, args.network_id
    )
    # generate an object that has all of the indices for the correct ibd format
    indices = create_indices(args.format.lower())

    ##target gene region or variant position
    target_gene = split_target_string(args.target)

    for clstID, id_dict in network_ids.items():
        # generate output path for the dendrogram image
        logger.info(f"generating dendrogram for network {clstID}")
        args.output.mkdir(parents=True, exist_ok=True)

        full_output_path = args.output / f"network_{clstID}_dendrogram.png"

        id_list = id_dict["ids"]
        haplotype_list = id_dict["haplotypes"]

        filter_obj: IbdFilter = IbdFilter.load_file(args.ibd, indices, target_gene)

        # choosing the proper way to filter the ibd files
        filter_obj.set_filter(args.segment_overlap)
        # Filter the IBD data to only the sites that were used in the DRIVE analysis
        filter_obj.preprocess(args.min_cm, id_list)

        ibd_segments = filter_obj.ibd_pd
        print(ibd_segments)

        # We need to make sure that the we are look at only the
        # right haplotypes
        haplotype_filtered_ibd_segments = ibd_segments[
            (ibd_segments.hapid1.isin(haplotype_list))
            & (ibd_segments.hapid2.isin(haplotype_list))
        ]

        haplotype_filtered_ibd_segments = haplotype_filtered_ibd_segments.rename(
            columns={
                indices.id1_indx: "pair_1",
                indices.id2_indx: "pair_2",
                indices.cM_indx: "length",
            }
        )

        print(haplotype_filtered_ibd_segments)

        matrix_id_list, distance_matrix = make_distance_matrix(
            haplotype_filtered_ibd_segments[["pair_1", "pair_2", "length"]], args.min_cm
        )

        if args.keep_temp:
            temp_dir = args.output / f"network_{clstID}_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)

            full_output_matrix_path = temp_dir / f"network_{clstID}_distance_matrix.txt"

            logger.info(
                f"recorded the distance matrix to the following path: {full_output_matrix_path}"
            )

            record_matrix(full_output_matrix_path, distance_matrix, matrix_id_list)

        dendrogram_array = generate_dendrogram(distance_matrix)

        logger.info(f"writing the output dendrogram to {full_output_path}")

        _ = draw_dendrogram(
            dendrogram_array,
            matrix_id_list,
            full_output_path,
            args.title,
            args.font_size,
        )
