namespace ObsidianPorter.Core.Models;

/// <summary>
/// Represents the result of an import operation.
/// </summary>
/// <param name="TotalNotes">Total number of notes processed.</param>
/// <param name="SuccessfulNotes">Number of notes successfully imported.</param>
/// <param name="FailedNotes">Number of notes that failed to import.</param>
public record ImportResult(
    int TotalNotes,
    int SuccessfulNotes,
    int FailedNotes
);
