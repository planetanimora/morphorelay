using UnrealBuildTool;

public class PerfBridgeMH : ModuleRules
{
    public PerfBridgeMH(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput", "LiveLinkInterface"
        });

        if (Target.bBuildEditor)
        {
            PrivateDependencyModuleNames.Add("AssetRegistry");
        }
    }
}
