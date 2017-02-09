"""
"""

# This file is part of genetest.
#
# This work is licensed under the Creative Commons Attribution-NonCommercial
# 4.0 International License. To view a copy of this license, visit
# http://creativecommons.org/licenses/by-nc/4.0/ or send a letter to Creative
# Commons, PO Box 1866, Mountain View, CA 94042, USA.


from pyplink import PyPlink

from .core import (GenotypesContainer, Representation, MarkerGenotypes,
                   MarkerInfo)


__copyright__ = "Copyright 2016, Beaulieu-Saucier Pharmacogenomics Centre"
__license__ = "Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)"


__all__ = ["PlinkGenotypes"]


class PlinkGenotypes(GenotypesContainer):
    def __init__(self, prefix, representation):
        """Instantiate a new PlinkGenotypes object.

        Args:
            prefix (str): the prefix of the Plink binary files.
            representation (str): A valid genotype representation format (e.g.
                                  genotypes.core.REPRESENTATION.ADDITIVE).

        """
        # Checking the representation
        self.check_representation(representation)
        if representation == Representation.DOSAGE:
            raise ValueError("{} is an invalid representation for genotyped "
                             "data (it is usually used for imputed "
                             "data)".format(representation.upper()))
        self._representation = representation

        self.bed = PyPlink(prefix)
        self.bim = self.bed.get_bim()
        self.fam = self.bed.get_fam()

        # We want to set the index for the FAM file
        try:
            self.fam = self.fam.set_index("iid", verify_integrity=True)

        except ValueError:
            self.fam["fid_iid"] = [
                "{fid}_{iid}".format(fid=fid, iid=iid)
                for fid, iid in zip(self.fam.fid, self.fam.iid)
            ]
            self.fam = self.fam.set_index("fid_iid", verify_integrity=True)

    def close(self):
        pass

    def __repr__(self):
        """The string representation."""
        return "PlinkGenotypes({:,d} samples; {:,d} markers)".format(
            self.get_nb_samples(),
            self.get_nb_markers(),
        )

    def get_genotypes(self, marker):
        """Returns a dataframe of genotypes encoded using the provided model.

        Args:
            marker (str): A marker ID (e.g. rs123456).

        Returns:
            MarkerGenotypes: A named tuple containing the dataframe with the
            encoded genotypes for all samples (the index of the dataframe will
            be the sample IDs), the minor and major alleles.

        Note
        ====
            PyPlink returns the genotypes in the additive format. So we only
            require to convert to genitypic representation if required.

        Note
        ====
            If the sample IDs are not unique, the index is changed to be the
            sample family ID and individual ID (i.e. fid_iid).

        """
        # Returning the genotypes
        return self._create_genotypes(
            marker=marker,
            genotypes=self.bed.get_geno_marker(marker),
        )

    def iter_marker_genotypes(self):
        """Iterates on available markers.

        Returns:
            MarkerGenotypes: A named tuple containing the dataframe with the
            encoded genotypes for all samples (the index of the dataframe will
            be the sample IDs), the minor and major alleles.

        Note
        ====
            If the sample IDs are not unique, the index is changed to be the
            sample family ID and individual ID (i.e. fid_iid).

        """
        # Iterating over all markers
        for marker, genotypes in self.bed.iter_geno():
            yield self._create_genotypes(
                marker=marker,
                genotypes=genotypes,
            )

    def iter_marker_info(self):
        """Iterate over marker information."""
        for idx, row in self.bim.iterrows():
            yield MarkerInfo(
                row.name, row.chrom, row.pos, a1=row.a1, a2=row.a2
            )

    def _create_genotypes(self, marker, genotypes):
        """Creates the genotype dataframe from an binary Plink file.

        Args:
            marker (str): The name of the marker.
            genotypes (numpy.ndarray): The genotypes.

        Returns:
            pandas.DataFrame: The genotypes in the required representation.
        """
        # Getting and formatting the genotypes
        additive = self.create_geno_df(
            genotypes=genotypes,
            samples=self.fam.index,
        )

        # Checking the format is fine
        additive, minor, major = self.check_genotypes(
            genotypes=additive,
            minor=self.bim.loc[marker, "a1"],
            major=self.bim.loc[marker, "a2"],
        )

        chrom, pos = self.bim.loc[marker, ["chrom", "pos"]].values
        info = MarkerInfo(marker, chrom, pos, a1=minor, a2=major,
                          minor=MarkerInfo.A1)

        # Returning the value as ADDITIVE representation
        if self._representation == Representation.ADDITIVE:
            return MarkerGenotypes(info, additive)

        # Returning the value as GENOTYPIC representation
        if self._representation == Representation.GENOTYPIC:
            return MarkerGenotypes(info, self.additive2genotypic(additive))

    def get_nb_samples(self):
        """Returns the number of samples.

        Returns:
            int: The number of samples.

        """
        return self.bed.get_nb_samples()

    def get_nb_markers(self):
        """Returns the number of markers.

        Returns:
            int: The number of markers.

        """
        return self.bed.get_nb_markers()
