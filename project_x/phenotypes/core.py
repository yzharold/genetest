"""
"""


# This file is part of project_x.
#
# This work is licensed under the Creative Commons Attribution-NonCommercial
# 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.


__copyright__ = "Copyright 2016, Beaulieu-Saucier Pharmacogenomics Centre"
__license__ = "Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)"


__all__ = ["PhenotypesContainer"]


class PhenotypesContainer(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        raise NotImplementedError()

    @classmethod
    def get_required_arguments(cls):
        """Returns the required arguments.

        Returns:
            tuple: The required arguments of the phenotype container.

        """
        return cls._required_args

    @classmethod
    def get_optional_arguments(cls):
        """Returns the optional arguments.

        Returns:
            dict: The optional arguments (with default values) of the
                  phenotype container.

        """
        return cls._optional_args

    def get_phenotypes(self):
        """Returns a dataframe of phenotypes.

        Returns:
            pandas.DataFrame: A dataframe containing the phenotypes (with the
                              sample IDs as index).

        """
        raise NotImplementedError()
