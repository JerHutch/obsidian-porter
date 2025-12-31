namespace ObsidianPorter.Core.Models;

/// <summary>
/// Configuration for the import process.
/// </summary>
public class ImportConfig
{
    // Phase 2 Features
    public bool EnableEditorPipeline { get; set; } = true;
    public bool EnableAutoTagging { get; set; } = true;
    public bool EnableFolderOrganization { get; set; } = true;
    public bool EnableContentTransformation { get; set; } = true;

    // Phase 3 Features
    public bool EnableNoteSplitting { get; set; } = false;

    // LLM Categorization
    public bool EnableLlmCategorization { get; set; } = false;
    public string LlmProvider { get; set; } = "openai";
    public string? LlmModel { get; set; }
    public Dictionary<string, string> LlmApiKeys { get; set; } = new();
    public string? LlmBaseUrl { get; set; }
    public int LlmTimeoutSec { get; set; } = 30;
    public int LlmMaxRetries { get; set; } = 2;
    public int LlmConcurrency { get; set; } = 4;
    public bool LlmCacheEnabled { get; set; } = true;
    public string LlmCachePath { get; set; } = ".cache/llm_category.jsonl";
    public double LlmMinConfidence { get; set; } = 0.6;
    public int LlmHeadChars { get; set; } = 2500;
    public int LlmTailChars { get; set; } = 500;
    public string UndecidedPolicy { get; set; } = "suggest";
    public int SuggestionsCount { get; set; } = 3;
    public bool PropagateCategoryTag { get; set; } = true;
    public bool PropagateSuggestedCategoriesWhenOther { get; set; } = true;
    public bool PropagateLlmSuggestedTags { get; set; } = true;
    public string? LlmPromptTemplatePath { get; set; }
    public string LlmPromptVersion { get; set; } = "v1";
    public bool LlmAllowFreeformSuggestions { get; set; } = true;
    public bool LlmSuggestTags { get; set; } = true;
    public int LlmTagsMaxCount { get; set; } = 5;
    public int LlmTagsMinCount { get; set; } = 0;

    public List<CategoryDefinition> Categories { get; set; } = new()
    {
        new("Cocktails", "cocktails", "Cocktail recipes, mixed drinks, ingredients, techniques."),
        new("Recipes", "recipes", "Food recipes, ingredients, cooking instructions."),
        new("Gaming", "gaming", "Video games, gameplay notes, walkthroughs, strategies."),
        new("Music", "music", "Music notes, artists, songs, albums, playlists."),
        new("Track lists", "track-lists", "Tracklists, DJ sets, setlists, ordered lists of tracks."),
        new("House", "house", "Home ownership and maintenance: projects, repairs, appliances, upkeep."),
        new("Role-playing games", "role-playing-games", "Tabletop RPGs, characters, campaigns, rules."),
        new("Cisco", "cisco", "Networking/Cisco notes, configs, commands."),
        new("Other", "other", "Fallback category for low-confidence or uncategorized notes.")
    };

    // Organization Settings
    public bool OrganizeByFolder { get; set; } = true;
    public string FolderStructure { get; set; } = "tags"; // "tags", "date", "custom", "flat"
    public bool CreateIndexFiles { get; set; } = false;

    // Tagging Settings
    public Dictionary<string, List<string>> AutoTagRules { get; set; } = new();
    public List<string> TagBlacklist { get; set; } = new();
    public List<string>? TagWhitelist { get; set; }

    // Content Processing
    public bool CleanWhitespace { get; set; } = true;
    public bool StandardizeHeaders { get; set; } = true;
    public bool FixListFormatting { get; set; } = true;

    // Output Settings
    public string OutputFormat { get; set; } = "obsidian";
    public bool PreserveOriginalStructure { get; set; } = false;
    public bool CreateBacklinks { get; set; } = false;

    // Custom Rules
    public Dictionary<string, List<string>> CustomTagRules { get; set; } = new();
    public Dictionary<string, string> CustomFolderRules { get; set; } = new();
    public Dictionary<string, string> CustomTransformations { get; set; } = new();

    // Note Splitting Settings
    public int SplitHeaderLevel { get; set; } = 2;
    public bool PreserveMainHeader { get; set; } = true;
    public List<string> SplitNotesPatterns { get; set; } = new();
    public List<string> SplitEnabledTags { get; set; } = new() { "cocktails", "recipes", "drinks" };
}

/// <summary>
/// Represents a category definition for LLM-based categorization.
/// </summary>
/// <param name="Name">Display name of the category.</param>
/// <param name="Slug">URL-friendly slug for the category.</param>
/// <param name="Description">Description of what belongs in this category.</param>
public record CategoryDefinition(string Name, string Slug, string Description);
