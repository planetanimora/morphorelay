#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "M4AssetBootstrap.generated.h"

class USkeleton;

/** Editor-only asset bootstrap exposed to the project Python scripts. */
UCLASS()
class PERFBRIDGEMH_API UM4AssetBootstrap : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Planet Animora|M4")
    static USkeleton* CreateBaseSkeleton(const FString& AssetPath);
};
