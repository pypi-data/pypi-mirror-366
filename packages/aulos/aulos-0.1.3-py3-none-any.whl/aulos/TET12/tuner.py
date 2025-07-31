from aulos._core import BaseTuner

from .note import Note
from .utils import fivelimit_tuning_table, standard_tuning_table


class JustIntonationTuner(
    BaseTuner[Note],
    ratios=fivelimit_tuning_table(),
    reference_notenumber=60,
    note=Note,
):
    """
    Just Intonation Tuner (Five-limit tuning)

    * This tuner is based on the Just Intonation system, which utilizes simple
      whole-number ratios derived from the harmonic series.
    * It uses the Five-limit tuning ratios to determine the intervals between notes.
    * The system focuses on creating pure, consonant intervals, especially for
      natural harmonics.
    """


class MeantoneTuner(
    BaseTuner[Note],
    ratios=standard_tuning_table(5**0.25),
    reference_notenumber=60,
    note=Note,
):
    """
    Meantone Tuner

    * This tuner is based on the Meantone temperament, which aims to improve the
      consonance of the major third interval, often sacrificing the purity of other
      intervals like the perfect fifth.
    * Meantone tuning is typically used in historical or specific stylistic music
      applications where certain intervals are emphasized.
    """


class PythagoreanTuner(
    BaseTuner[Note],
    ratios=standard_tuning_table(1.5),
    reference_notenumber=60,
    note=Note,
):
    """
    Pythagorean Tuner

    * This tuner follows the Pythagorean tuning system, which is based on the
      harmonic series, emphasizing the pure perfect fifth (3:2 ratio).
    * The system uses the Pythagorean comma to create a series of intervals
      derived from the natural harmonic series.
    """


class Equal12Tuner(
    BaseTuner[Note],
    ratios=standard_tuning_table(2 ** (1 / 12)),
    reference_notenumber=60,
    note=Note,
):
    """
    Equal 12-Tone Tuner (12-TET)

    * This tuner uses the Equal Temperament system, where the octave is divided
      into 12 equal steps (12-TET).
    * It is the standard tuning system used in Western music, where all semitones
      are equal in frequency ratio.
    * This system allows instruments to play in all keys with equal tuning accuracy.
    """
