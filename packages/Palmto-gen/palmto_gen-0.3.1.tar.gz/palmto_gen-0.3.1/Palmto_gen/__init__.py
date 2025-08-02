import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
import scipy
import math

import numpy as np
from geopy.distance import geodesic as GD
from shapely.geometry import box
from shapely.geometry import LineString, Point
import shapely
from collections import defaultdict


import folium
from IPython.display import display, HTML
import random


def convert_to_points(coord_list):
    """Convert coordinate pairs into Shapely Point object.

    Args:
        coord_list(list): coordinate pairs in (lon, lat) format.

    Returns:
        list: coordinates-converted Shapely points. 
    """
    return [Point(coord) for coord in coord_list]

def process_data(df):
    """Convert list-formatted trajectories to individal Shapely Point.

    Args:
        df(pd.DataFrame): an object that contains at least a "geometry" column.

    Returns:
        gpd.GeoDataFrame: an object compliant with WGS84 reference system, ie. (lon, lat) pairs.
    """
    tqdm.pandas()
    df['geometry'] = df['geometry'].progress_apply(convert_to_points)
    df_points = df.explode('geometry')
    gdf = gpd.GeoDataFrame(df_points, geometry='geometry',crs="EPSG:4326")

    return gdf

class ConvertToToken:
    def __init__(self, df, area, cell_size):
        """Initialize a class object.
        
        Args:
            df(dataframe):  an object containing at least a 'geometry' column, 
                            with each row being a list of coordinate pairs in (lon, lat) format.
            area(gpd.GeoDataFrame): Shapely polygon delimiting the boundary of a geographical region.
            cell_size(int): side length of a square cell in an area grid.

        """
        self.cell_size = cell_size
        self.gdf = process_data(df)
        self.area = area

    def create_grid(self):
        """Creates a grid of cell size 'n' over a given area.

        Generates a regular grid of cells with the specified cell size (in meters)
        covering the entire bounding box of the study area. The grid cells are 
        created as Shapely box geometries and stored in a GeoDataFrame.
        
        This method converts the cell size from meters to degrees based on the
        geographic location, accounting for the Earth's curvature.

        Returns: 
                tuple: A tuple containing:
                    - cell(gpd.GeoDataFrame): object with grid cells as box 
                        geometries in the 'geometry' column. CRS is EPSG:4326.
                    - n_rows(int): number of rows in the grid.
                    - cell.shape[0]: total number of cells created.
        """
        # Geographical boundary delimited by (min_lon, min_lat, max_lon, max_lat)
        xmin, ymin, xmax, ymax = self.area.total_bounds
        
        # Calculate distance between two coordinate points of [lat, lon] in meter
        height = GD((ymin, xmax), (ymax, xmax)).m
        width = GD((ymin, xmin), (ymin, xmax)).m

        # how many cells across and down
        grid_cells = []
        
        # Compute number of cells along height
        n_cells_h = height / self.cell_size
        # Convert cell back to degree unit
        cell_size_h = (ymax - ymin) / n_cells_h

        n_cells_w = width / self.cell_size
        cell_size_w = (xmax - xmin) / n_cells_w

        for x0 in np.arange(xmin, xmax, cell_size_w):
            n_rows = 0
            for y0 in np.arange(ymin, ymax, cell_size_h):
                # bounds
                x1 = x0 + cell_size_w
                y1 = y0 + cell_size_h
                grid_cells.append(shapely.geometry.box(x0, y0, x1, y1))
                n_rows += 1
                # print('n_rows ', n_rows)

        cell = gpd.GeoDataFrame(grid_cells, columns=['geometry'], crs="EPSG:4326")
        print('Number of created cells: ', cell.shape[0])

        return cell, n_rows,  cell.shape[0]

    def assign_ids(self, grid, n_rows):
        """Assign each cell an unique ID.

        Assignes each grid cell a unique identifier based on its position in the grid. 
        IDs are tuples of (column_index, row_index) starting from 0. The assignment follows
        column-major order.

        Args:
            grid(gpd.GeoDataFrame): area grid returned from create_grid()
            n_rows: number of rows in the grid

        Returns:
            grid(gpd.GeoDataFrame): The input object with an additional "ID" column where each row
            contains a tuple of (col_index, row_index) for each cell.
        """
        total = grid.shape[0]
        n_cols = int(total / n_rows)

        tuple_list = []
        for i in range(n_cols):
            for j in range(n_rows):
                tuple_list.append(tuple((i, j)))
        grid['ID'] = tuple_list

        return grid

    def find_grid_center(self, grid):
        """Finds the centroid of each cell in the grid
        
        Calculates the geometric center point of each grid cell. It first projects the grid 
        to a flat plane using EPSG:3857 reference system for accurate geometric calculation,
        then converts the result back to EPSG:4326 system to maintain consistency with the
        original reference system.

        Args:
            grid(gpd.GeoDataFrame): an object with cell geometry and ID columns.

        Returns:
            grid_center(gpd.GeoDataFrame): a new object with "geometry" and "ID" columns. The former
            now represents a cell box with its centroid. 
        """
        grid_center = gpd.GeoDataFrame(columns=["geometry", "ID"], geometry='geometry', crs="EPSG:4326")

        grid_projected = grid.to_crs("EPSG:3857")
        centroids = grid_projected.centroid

        centroids_4326 = centroids.to_crs("EPSG:4326")

        grid_center['geometry'] = list(centroids_4326)
        grid_center["ID"] = grid["ID"]

        return grid_center
    
    def merge_with_polygon(self, grid):
        """Performs spatial joins between trajectory points and grid cells.

        Assigns each trajectory point to its corresponding grid cell using a spatial join
        operation. Points are matched to grid cells based on which cell polygon they fall 
        within. Points that don't fall within any grid cell are removed from the result

        Args:
            grid(gpd.GeoDataFrame): an object with cell geometry and ID columns.
        
        Returns:
            merged_df(gpd.GeoDataFrame): the trajectory points GeoDataFrame with additional "ID" 
            column containing grid cell ID where each point is located. 
        """
        # Include coords right on edge of grid by setting predicate to intersects
        merged_gdf = gpd.sjoin(self.gdf, grid, how='left', predicate='within')
        merged_gdf.drop(columns=['index_right'], inplace=True)
        
        # Drop any rows with 'nan' values in 'ID' column
        merged_gdf = merged_gdf.dropna(subset=['ID'])
        return merged_gdf
        
    def create_tokens(self):
        """Convert raw coordinate pairs into tokens of (row_id, col_id).

        Creates a grid over a given area where trajectories are sourced, assign unique IDs 
        to cells in the grid, compute cell centers and merge original coordinates with their
        corresponding cell IDs based on which cell they fall into.

        Returns: 
                tuple: A tuple containing:
                    - grid_center(gpd.GeoDataFrame): object containing a "geometry" and "ID" column, with 
                        the former representing a cell by its centroid.
                    - grouped_df(pd.DataFrame): object containing three columns -- "trip_id", "geometry"
                        and "ID". "geometry" represents a trajectory with a sequence of Point objects. 
        """
        grid, n_rows, num_cells = self.create_grid()
        assigned_grid = self.assign_ids(grid, n_rows)

        grid_center = self.find_grid_center(assigned_grid)
        merged_gdf = self.merge_with_polygon(grid)


        agg_funcs = {'geometry': list, 'ID':list}  
        grouped_df = merged_gdf.groupby('trip_id').agg(agg_funcs)

        sentences = grouped_df['ID'].tolist()
        sentences = [[x for i, x in enumerate(lst) if i == 0 or x != lst[i - 1]] for lst in sentences]

        
        return grid_center, grouped_df
    
class NgramGenerator:
    def __init__(self, sentence_gdf):
        """Initialize the NgramGenerator with trajectories represented as grid cell sequences.

        Args:
            sentence_gdf(pd.DataFrame): A pandas DataFrame containing trajectory data where
                each row represents a trip. Must have an 'ID' column containing lists of 
                tuples, where each tuple represents a grid cell coordinate (column, row) 
                that the trajectory passes through. This is typically the output from 
                ConvertToToken.create_tokens().
        
        """
        self.sentences = sentence_gdf['ID'].values.tolist()

    def find_start_end_points(self):
        """Extract start and end bigrams from trajectory sequences.

        Identifies the starting and ending positions of every trajectory by extracting the first
        and last two grid cells. Duplicate consecutive cells are first removed to ensure meaningful
        start/end points.

        Returns:
            start_end_points(list): a list of lists. Each inner contains two tuples: the first one
                represents the start bigram of a trip and the second one the end bigram of a trip.
                Only trips with more than three unique consecutive cells are included in the result.

        
        """
        sentences = [[x for i, x in enumerate(lst) if i == 0 or x != lst[i - 1]] for lst in self.sentences]
        
        start_end_points = []
        for sentence in sentences:
            if len(sentence) > 3:
                start_end_points.append([tuple((sentence[0], sentence[1])), tuple((sentence[-2], sentence[-1]))])

        return start_end_points
    
    def reverse_sentences(self, sentences):
        """Reverse trajectory sequences.

        Args:
            sentences(list): a list of lists, with the inner list consisting of a sequence of cell IDs.
        
        Returns:
            reversed_sentences(list): a list of lists, with the inner list not containing a reversed version 
                of original sequences.
        
        """
        reversed_sentences = []
        for sent in sentences:
            reverse = sent[::-1]
            reversed_sentences.append(reverse)

        return reversed_sentences

    def create_ngrams(self):
        """Extract bigrams and trigrams from the original and reversed trajectory sequences.

        Sentences, converted to list from the "ID" column of input dataframe, are reversed before bigrams and trigrams
        are extracted from both the original and reversed sentences. Each bigram dictionary also keeps count of unqiue
        bigram and trigrams. 

        Returns:
            ngrams(dict): a dictionary of four dictionaries. Each inner dictionary is comprised of items that
            has a tuple of cell IDs as its key and its number of occurance as the value.
            start_end_points(list): a list of lists, as returned by find_start_end_points().

        """
        start_end_points = self.find_start_end_points()
        sentences_reversed = self.reverse_sentences(self.sentences)
        # corpus = self.sentences + sentences_reversed

        bigrams_reversed = {}
        trigrams_reversed = {}

        for sentence in tqdm(sentences_reversed):
            # for word in sentence:
            #     unigram_counts[word] = unigram_counts.get(word, 0) + 1
            #     self.total_unigrams += 1

            for i in range(len(sentence) - 1):
                bigram = (tuple(sentence[i:i+2]))
                bigrams_reversed[bigram] = bigrams_reversed.get(bigram, 0) + 1

            for i in range(len(sentence) - 2):
                trigram = (tuple(sentence[i:i+3]))
                trigrams_reversed[trigram] = trigrams_reversed.get(trigram, 0) + 1
        
        bigrams_original = {}
        trigrams_original = {}
        for sentence in tqdm(self.sentences):

            for i in range(len(sentence) - 1):
                bigram = (tuple(sentence[i:i+2]))
                bigrams_original[bigram] = bigrams_original.get(bigram, 0) + 1

            for i in range(len(sentence) - 2):
                trigram = (tuple(sentence[i:i+3]))
                trigrams_original[trigram] = trigrams_original.get(trigram, 0) + 1

        print(f"\nNumber of Unique Bigrams: {len(bigrams_original)} \nNumber of Unique Trigrams: {len(trigrams_original)}")

        ngrams = {
            'bigrams_original': bigrams_original,
            'bigrams_reversed': bigrams_reversed,
            'trigrams_original': trigrams_original,
            'trigrams_reversed': trigrams_reversed
        }

        return  ngrams, start_end_points
 
def process_trigrams(trigrams):
    """Arrange trigram tuples and their count of occurance in a different format.

    Create a dictionary that has the first two tokens in a trigram tuple as its key and the last token, 
    as well as the occurance count of the trigram as its value. This arrangement facilitates next-point 
    prediction through a statistical approach. 

    Args:
        trigrams(dict): a dictionary of trigram tuples and their occurance count in the format of
            {(token_1, token_2, token_3): count}.
    
    Returns:
        trigrams_dict(dict): an rearranged trigram dictionary, formatted as {(token_1, token_2): [(token_3, conut), ...]}
    
    """
    trigrams_dict = defaultdict(list)
    for trigram, count in trigrams.items():
        first_two_tokens = trigram[:2]
        third_token = trigram[2]
        trigrams_dict[first_two_tokens].append((third_token, count))
    return trigrams_dict

def process_trigrams_2(trigrams):
    """Reorganizes trigrams in an alternative format.

    Transforms a trigram dictionary into a lookup structure where pairs of (first_token, third_token)
    are mapped to a list of second_tokens. This is useful for finding "bridge" points between two 
    non-adjacent grid cells.

    Args:
        trigrams(dict): a dictionary of trigram tuples and their occurance count in the format of
            {(token_1, token_2, token_3): count}.

    Returns:
        trigram_dict_2(dict): a dictionary mapping (first_token, third_token) tuples to a list of 
            middle tokens.
        
    """
    trigram_dict_2 = defaultdict(list)
    for trigram in trigrams.keys():
        trigram_dict_2[(trigram[0]), trigram[-1]].append(trigram[1])

    return trigram_dict_2

class TrajGenerator:
    def __init__(self, ngrams, start_end_points, n, grid):
        """Initialize a generator with ngrams and grid information.

        Args:
            ngrams(dict): dictionary mapping ngrams to their frequency:
                -'trigrams_original': dict mapping trigram tuples to their counts;
                -'trigrams_reversed': dict mapping reversed trigram tuples to their counts;
                -'bigrams_original': dict mapping bigram tuples to their counts;
                -'bigrams_reversed': dict mapping reversed bigram tuples to their counts;
            start_end_points(list): list of tuples where each tuple contains:
                -first element: a tuple of (first_point, second_point);
                -second element: a tupe of (second_to_last_point, last_point);
            n(int): number of trajectories to generate;
            grid(gpd.GeoDataFrame): GeoDataFrame containing grid cell information with columns:
                -'geometry': Shapely Point objects representing cell centroids;
                -'ID': tuple identifiers (row, col) for each grid cell;
        
        """
        # Count the number of occurance of each unique trigrams in both original and reversed versions
        self.trigrams = {key: ngrams['trigrams_original'].get(key, 0) + ngrams['trigrams_reversed'].get(key, 0) for key in set(ngrams['trigrams_original']) | set(ngrams['trigrams_reversed'])}

        self.trigram_dict = process_trigrams(self.trigrams)
        self.trigram_dict_original= process_trigrams(ngrams['trigrams_original'])
        self.trigrams_dict_2 = process_trigrams_2(self.trigrams)
        self.start_end_points = start_end_points
        self.grid_center = grid
        self.num_sentences = n
        self.k = 3

    @staticmethod
    def start_path(start, end):
        """Create an initial 4-point trajectory by inserting closest points in the middle.

        This method finds the two points (one from start and one from end) that are closest to each other in
        Euclidean space, then arranges all four points to form a smooth initial segment.

        Agrs:
            start(tuple): a tuple of two points representing the start of a trip:
                - First point: starting point as (x, y) coordinates
                - Second point: second point as (x, y) coordinates
            end(tuple): a tuple of two points representing the end of a trip:
                - First point: second-to-last point as (x, y) coordinates
                - Second point: last point as (x, y) coordinates
        
        Returns:
            path_start(list): an intial trip segment of (outer_point1, close_point1, close_point2, outer_point2).
        """
        min_distance = float('inf')
        closest_pair = None

        # Calculate the Euclidean distance between each pair of points (one from each list)
        for point1 in start:
            for point2 in end:
                dist = scipy.spatial.distance.euclidean(point1, point2)
                if dist < min_distance:
                    min_distance = dist
                    closest_pair = (point1, point2)


        path_start = [point for point in start + end if point not in closest_pair]

        path_start.insert(1, closest_pair[0])
        path_start.insert(2, closest_pair[-1])

        return path_start

    @staticmethod
    def calculate_distance(point1, point2):
        """Calculate the Euclidean distance between two points in a 2D plane.

        Args:
            point1(tuple): first point as a tuple of (x, y) coordinates;
            point2(tuple): second point as a tuple of (x, y) coordinates;

        Returns:
            Float: always returns a non-negative value.
        
        """
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def find_next_tokens(self, left, right, path_sentence):
        """Find the next token pairs to extend a trajectory by analysing trigram frequency and spatial distance

        This method identifies potential next tokens for both left and right sides of a growing trajectory. It uses
        trigram frequency data to find the next probable points, then selects token pairs based on their spatial 
        proximity to maintain coherence. This method ensures no repeated tokens in the path.

        Args:
            left(list): a list of two tokens representing left edge of current path;
            right(list): a list of two tokens representing right edge of current path;
            path_sentence(list): current path as a list of tokens. Used to prevent selecting tokens that would create 
                loops in a trajectory;
        
        Returns:
            points(list): a list of 3 token pairs, where each element is a token of ((left_point, right_point)) that 
                represents an extension of current path.
        """
        next_tokens_l = dict(self.trigram_dict.get(tuple(left), []))
        next_tokens_r = dict(self.trigram_dict.get(tuple(right), []))

        next_tokens_with_counts_l = {key: value for key, value in next_tokens_l.items() if key not in path_sentence}
        next_tokens_with_counts_r = {key: value for key, value in next_tokens_r.items() if key not in path_sentence}

        sorted_next_tokens_l = sorted(next_tokens_with_counts_l.items(), key=lambda x: x[1], reverse=True)
        sorted_next_tokens_l_top_k = sorted_next_tokens_l[:self.k] if len(sorted_next_tokens_l) >= self.k else sorted_next_tokens_l

        sorted_next_tokens_r = sorted(next_tokens_with_counts_r.items(), key=lambda x: x[1], reverse=True)
        sorted_next_tokens_r_top_k = sorted_next_tokens_r[:self.k] if len(sorted_next_tokens_r) >= self.k else sorted_next_tokens_r

        closest_points = {}

        for point1, _ in sorted_next_tokens_l_top_k:
            for point2, _ in sorted_next_tokens_r_top_k:
                distance = TrajGenerator.calculate_distance(point1, point2)
                closest_points[(point1, point2)] = distance

        closest_points_top3 = dict(sorted(closest_points.items(), key=lambda x: x[1], reverse=False)[:self.k])

        points = list(closest_points_top3.keys())
        return points

    def generate_sentences_using_origin_destination(self):
        """Generate a complete trajectory by connecting origin and destination points through spatial proximity.

        This method creates a trajectory by starting with randomly selected origin-destination pairs
        and iteratively filling in the path between them. It uses a bidirectional growth approach,
        extending from both ends simultaneously while maintaining spatial coherence through trigram
        frequencies and distance minimization. The process continues until the growing ends meet
        close enough that they can be connected by a single intermediate token.

        Returns:
            path_sentence(list): A complete trajectory as a list of tokens (coordinate tuples) representing
                a path from origin to destination. Returns empty list if unable to generate
                a valid path after 3 attempts.    
        
        """
        full_sentence = False

        random_path = random.choice(self.start_end_points)
        start = random_path[0]
        end = random_path[1]

        num_tries = 0
        while not full_sentence:
            path_start = self.start_path(start, end)
            left = path_start[:2]
            right = path_start[-2:]

            path_sentence = path_start
            for i in range(40):

                points = self.find_next_tokens(left, right, path_sentence)
                try:
                    j = random.randint(0, len(points)-1)
                except:
                    continue

                left = [left[-1], points[j][0]]
                right = [right[-1], points[j][1]]

                path_sentence.insert(i+2, left[-1])
                path_sentence.insert(i+3, right[-1])

                # Check if a trigram that matches the left and righ tokens exists in the trigram corpus. 
                # If one exists, the points are close enough and a full 'sentence' is constructed
                if len (self.trigrams_dict_2[left[-1], right[-1]]) > 1:
                    fills = self.trigrams_dict_2[left[-1], right[-1]]

                    trigram_fills = {}
                    for each in fills:
                        trigram = tuple((left[-1], each, right[-1]))
                        trigram_fills[trigram] = self.trigrams[trigram]

                    trigram_with_highest_count = max(trigram_fills, key=lambda k: trigram_fills[k])

                    path_sentence.insert(i+3, trigram_with_highest_count[1])
                    full_sentence = True
                    break
            
            if full_sentence:
                return path_sentence

            num_tries += 1
            if num_tries == 3:
                return []     

    def generate_sentences_using_origin(self, length, seed=None):
        """Generate a trajectory of specified length starting from a random origin point using trigram language model.

        Creates a trajectory by starting with an origin point pair and extending it token by token
        using weighted random selection based on trigram frequencies. This method follows a 
        traditional n-gram language model approach where the next token is probabilistically 
        chosen based on the frequency distribution of observed trigrams in the training data.  
      

        Args:
            length (int): Target length of the trajectory in number of tokens/points.
                The actual length may be shorter if no valid continuations exist.
            seed (int, optional): Random seed for reproducible trajectory generation.
                If provided, ensures deterministic origin selection from available
                start points. Defaults to None for random selection.
        
        Returns:
            text(list): A trajectory as a list of tokens (coordinate tuples), starting from
                the selected origin. Length will be min(length, available_path_length).
                May be shorter than requested if the trajectory reaches a dead end.
        """
        text = []
        if seed is not None:
            random.seed(seed)
            current_trigram = random.sample(self.start_end_points, min(len(self.start_end_points), self.num_sentences))[0][0]
        else:
            current_trigram = random.choice(self.start_end_points)[0]
        
        text.extend(current_trigram)

        while len(text) < length:
            # Get the list of next tokens and their counts for the current trigram
            next_tokens_with_counts = self.trigram_dict_original.get(current_trigram, [])
            if not next_tokens_with_counts:
                break  

            # Choose the next token based on its counts
            total_count = sum(count for _, count in next_tokens_with_counts)
            random_value = random.randint(1, total_count) 
            cumulative_count = 0
            next_token = None

            #pick the next token randomly from the possible next tokens
            for token, count in next_tokens_with_counts:
                cumulative_count += count
                if random_value <= cumulative_count:
                    next_token = token
                    break

            # Append the next token to the text
            text.append(next_token)

            # Update the current trigram
            current_trigram = current_trigram[1:] + (next_token,)

        return text

    def convert_sentence_to_traj(self, generated_sentences):
        """Convert tokenized trajectory sentences into geographic coordinate sequences.

        Transforms grid-based token representations (ID tuples) into actual geographic
        trajectories by mapping each token to its corresponding grid cell centroid. This
        creates smooth paths through the geographic space using the pre-computed cell
        center points stored in the grid_center GeoDataFrame.

        Args:
            generated_sentences (list): A list of trajectory sentences, where each sentence
                is a list of tokens. Each token is a tuple (column, row) representing a
                grid cell ID, e.g., [[(0,1), (1,1), (2,1)], [(3,3), (3,4), (4,4)]].
        
        Returns:
            all_points(list): A list of trajectories, where each trajectory is a list of Shapely Point
                objects representing the geographic coordinates. Each Point corresponds to
                the centroid of the grid cell identified by the token. Invalid tokens are
                silently skipped.
        
        """
        token_to_geometry = dict(zip(self.grid_center['ID'], self.grid_center['geometry']))
        all_points = []

        for sentence in tqdm(generated_sentences):
            sentence_geometries = [token_to_geometry[token] for token in sentence if token in token_to_geometry]
            all_points.append(sentence_geometries)

        return all_points

    def generate_trajs_using_origin_destination(self):
        """Generate synthetic trajectories using origin-destination pairs and return in multiple formats.

        Creates a specified number of synthetic trajectories by repeatedly calling the origin-destination
        generation algorithm. Each trajectory connects randomly selected start and end points through
        spatially coherent paths. The method ensures all generated trajectories are valid (non-empty)
        and converts them from token sequences to geographic coordinates. Results are returned in
        two formats for different use cases.

        Returns:
            tuple: A pair of DataFrames containing the same trajectories in different formats:
                - df (DataFrame): Trajectories as coordinate lists with columns:
                    - 'trip_id': Unique identifier (1 to n)
                    - 'geometry': List of [x, y] coordinate pairs
                - gdf (GeoDataFrame): Trajectories as Shapely geometries with columns:
                    - 'trip_id': Unique identifier (1 to n)
                    - 'geometry': List of Shapely Point objects
        
        """
        new_generated_sentences = []
        with tqdm(total=self.num_sentences, desc="Generating sentences") as pbar:
            while len(new_generated_sentences) < self.num_sentences:
                path_sentence = self.generate_sentences_using_origin_destination()
                if path_sentence:
                    new_generated_sentences.append(path_sentence)
                    pbar.update(1) 

        new_trajs =  self.convert_sentence_to_traj(new_generated_sentences)

        geom_list = []
        for traj in new_trajs:
            coordinates = []
            for point in traj:
                coordinates.append([point.x, point.y])
            geom_list.append(coordinates)

        df = pd.DataFrame({'geometry':geom_list})
        df['trip_id'] = range(1, len(df) + 1)
        df = df[['trip_id', 'geometry']]

        gdf = pd.DataFrame({'geometry':new_trajs})
        gdf['trip_id'] = range(1, len(gdf) + 1)
        gdf = gdf[['trip_id', 'geometry']]

        return df, gdf

    def generate_trajs_using_origin(self, sentence_length, seed=None):
        """Generate synthetic trajectories of specified length from origin points and return in multiple formats.

        Creates a specified number of trajectories by repeatedly generating paths from randomly
        selected origin points using the trigram language model approach. Each trajectory extends
        from its origin for approximately the target length. The method filters out trajectories
        that are significantly shorter than requested (more than 5 tokens short) to ensure quality.
        Results are returned in two formats for different use cases.
        
        Args:
            sentence_length (int): Target length for each trajectory in number of tokens/points.
                Trajectories shorter than (sentence_length - 5) are rejected and regenerated.
            seed (int, optional): Random seed for reproducible batch generation.
                If provided, generates deterministic set of trajectories. Defaults to None
                for random generation.

        Returns:
            tuple: A pair of DataFrames containing the same trajectories in different formats:
                - df (DataFrame): Trajectories as coordinate lists with columns:
                    - 'trip_id': Unique identifier (1 to n)
                    - 'geometry': List of [x, y] coordinate pairs
                - gdf (DataFrame): Trajectories as Shapely geometries with columns:
                    - 'trip_id': Unique identifier (1 to n)
                    - 'geometry': List of Shapely Point objects
        """
        new_generated_sentences = []

        if seed is not None:
          random.seed(seed)
          random_seeds = [random.randint(1, len(self.start_end_points)) for _ in range(self.num_sentences)]

          with tqdm(total=self.num_sentences, desc="Generating sentences") as pbar:

              # while len(new_generated_sentences) < self.num_sentences:
              for seed in random_seeds:
                  generated_text = self.generate_sentences_using_origin(sentence_length, seed)
                  if len(generated_text) > (sentence_length-5):
                      new_generated_sentences.append(generated_text)
                      pbar.update(1)  # Update the progress bar
          
        else:
          with tqdm(total=self.num_sentences, desc="Generating sentences") as pbar:
              while len(new_generated_sentences) < self.num_sentences:
                  generated_text = self.generate_sentences_using_origin(sentence_length, seed)
                  if len(generated_text) > (sentence_length-5):
                      new_generated_sentences.append(generated_text)
                      pbar.update(1)  # Update the progress bar

        new_trajs =  self.convert_sentence_to_traj(new_generated_sentences)


        geom_list = []
        for traj in new_trajs:
            coordinates = []
            for point in traj:
                coordinates.append([point.x, point.y])
            geom_list.append(coordinates)

        df = pd.DataFrame({'geometry':geom_list})
        df['trip_id'] = range(1, len(df) + 1)
        df = df[['trip_id', 'geometry']]

        gdf = pd.DataFrame({'geometry':new_trajs})
        gdf['trip_id'] = range(1, len(gdf) + 1)
        gdf = gdf[['trip_id', 'geometry']]

        return df, gdf

class DisplayTrajs():
    def __init__(self, original_trajs, generated_trajs):
        """Initialize the DisplayTrajs visualization class with original and synthetic trajectories.

        Creates a visualization handler for comparing original (real) trajectories with 
        synthetically generated trajectories. This class provides methods to display 
        trajectories side-by-side on interactive maps and create heatmap visualizations 
        for spatial distribution analysis.

        Args:
            original_trajs(list): Original/real trajectories to visualize. Expected format is a list of 
                trajectories where each trajectory is a list of Shapely Point objects, 
                e.g., [[Point(x1,y1), Point(x2,y2), ...], ...].
            generated_trajs (list): Synthetically generated trajectories to compare.
                Expected format matches original_trajs - list of trajectories where each
                trajectory is a list of Shapely Point objects.
        
        """
        self.original_trajs = original_trajs
        self.generated_trajs =  generated_trajs

    def plot_map(self, trajs):
        """Creates an interactive Folium map displaying trajectory paths as polylines.

        Generates an interactive web map centered on the first trajectory point and 
        renders all trajectories as blue polylines. The map allows users to zoom, 
        pan, and explore the trajectory patterns interactively.

        Args:
            trajs (list): A list of trajectories where each trajectory is a list of 
                shapely Point objects or similar geometry objects with x (longitude) 
                and y (latitude) attributes. 

        Returns:
            folium.Map: A Folium map object containing all trajectories visualized 
                as blue polylines. The map can be displayed in Jupyter notebooks or 
                saved as HTML.
        
        """
        center_coords = (trajs[0][0].y, trajs[0][0].x)
        mymap = folium.Map(location=center_coords, zoom_start=12)

        for points in trajs:
            line = LineString(points)
            line_coords = [(point[1], point[0]) for point in line.coords]
            folium.PolyLine(locations=line_coords, color='blue').add_to(mymap)

        return mymap

    def display_maps(self):
        """Display original and generated trajectories side-by-side in interactive Folium maps.

        Creates two interactive maps showing original trajectories (left) and generated 
        trajectories (right) for visual comparison. Each trajectory is rendered as a blue 
        polyline on its respective map. The maps are displayed in a responsive HTML layout 
        within Jupyter notebooks or similar environments that support HTML rendering.
        
        """
        map1 = self.plot_map(self.original_trajs)
        map2 = self.plot_map(self.generated_trajs)

        html_map1 = map1._repr_html_()
        html_map2 = map2._repr_html_()

        html = f"""
        <div style="display: flex; justify-content: space-around;">
            <div style="width: 45%;">
                <h3 style="text-align: center;">Original Trajectories</h3>
                {html_map1}
            </div>
            <div style="width: 45%;">
                <h3 style="text-align: center;">Generated Trajectories</h3>
                {html_map2}
            </div>
        </div>
        """

        # Display the HTML
        display(HTML(html))

    def merge_grid_with_points(self, grid, df, num_cells):
        """Merges trajectory points with grid cells to determine which region each point belongs to.

        Performs a spatial join between trajectory points and grid cells, assigning each point
        to its corresponding grid region. The method explodes the trajectory DataFrame to 
        individual points, converts them to a GeoDataFrame, and then performs a spatial join
        with the grid to identify which grid cell contains each point.

        Args:
            grid (gpd.GeoDataFrame): A GeoDataFrame containing the grid cells with their 
                geometries. Each cell represents a spatial region.
            df (pd.DataFrame): A DataFrame containing trajectory data with a 'geometry' 
                column that contains lists of coordinate points for each trajectory.
            num_cells (int): The total number of cells in the grid. Used to assign 
                sequential region IDs from 0 to num_cells-1.

        Returns:
            gpd.GeoDataFrame: A merged GeoDataFrame where each row represents a single 
            trajectory point with the following additional columns:
                - 'Region': The ID of the grid cell containing the point
                - 'point_region': The geometry (polygon) of the grid cell containing the point, or 'nan' if the point doesn't fall within any grid cell.

        """
        grid['Region'] = [i for i in range(0, num_cells)]
        df = df.explode('geometry')

        gdf = gpd.GeoDataFrame(df, geometry='geometry', crs = "EPSG:4326")
        merged_df = gpd.sjoin(gdf, grid, how='left', predicate='within', lsuffix='_points', rsuffix='_grid')

        region_geometries = {i: grid.loc[i]['geometry'] for i in range(num_cells)}
        polygon_region = []

        for idx, row in tqdm(merged_df.iterrows(), total=len(merged_df)):
            region = row['Region']
            if region in region_geometries:
                polygon_region.append(region_geometries[region])
            else:
                polygon_region.append('nan')

        merged_df['point_region'] = polygon_region

        return merged_df

    def plot_heat_map(self, df, area, ax, cell_size):
        """Creates a heatmap visualization showing the density of trajectory points across grid cells.

        Generates a grid over the specified area, counts the number of trajectory points 
        falling within each grid cell, and visualizes this density as a heatmap using a 
        color gradient. The heatmap helps identify areas of high and low trajectory activity.

        Args:
            df (pd.DataFrame): A DataFrame containing trajectory data with a 'geometry' 
                column that contains lists of coordinate points for each trajectory.
            area (gpd.GeoDataFrame): A GeoDataFrame defining the geographical area to be 
                analyzed. Used to determine grid boundaries and overlay the area outline 
                on the plot.
            ax (matplotlib.axes.Axes): The matplotlib axes object on which to draw the 
                heatmap. Allows integration with existing figure layouts.
            cell_size (int): The side length of each grid cell in meters. Determines the 
                spatial resolution of the heatmap - smaller values create finer grids 
                with more detail.
        
        """
        TokenCreator = ConvertToToken(df, area, cell_size)
        grid, n_rows, num_cells = TokenCreator.create_grid()
        df = self.merge_grid_with_points(grid, df, num_cells)

        df_valid = df[df['point_region'] != 'nan']
        polygon_counts = df_valid['point_region'].value_counts()

        polygon_counts_df = pd.DataFrame({'geometry': polygon_counts.index, 'count': polygon_counts.values})
        polygon_counts_gdf = gpd.GeoDataFrame(polygon_counts_df)
        polygon_counts_gdf = polygon_counts_gdf.set_geometry('geometry')

        # Plotting the heatmap
        # fig, ax = plt.subplots(figsize=(10, 6))
        polygon_counts_gdf.plot(column='count', cmap='YlOrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
        area.plot(ax=ax, color = 'none')
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title('Generated Trajectories')