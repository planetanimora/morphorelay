#include "M4AssetBootstrap.h"

#include "Animation/Skeleton.h"

#if WITH_EDITOR
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/PackageName.h"
#include "ReferenceSkeleton.h"
#endif

USkeleton* UM4AssetBootstrap::CreateBaseSkeleton(const FString& AssetPath)
{
#if WITH_EDITOR
    if (!AssetPath.StartsWith(TEXT("/Game/")))
    {
        return nullptr;
    }

    const FString AssetName = FPackageName::GetShortName(AssetPath);
    const FString ObjectPath = AssetPath + TEXT(".") + AssetName;
    if (USkeleton* Existing = LoadObject<USkeleton>(nullptr, *ObjectPath))
    {
        return Existing;
    }

    UPackage* Package = CreatePackage(*AssetPath);
    if (!Package)
    {
        return nullptr;
    }

    USkeleton* Skeleton = NewObject<USkeleton>(Package, *AssetName, RF_Public | RF_Standalone);
    if (!Skeleton)
    {
        return nullptr;
    }

    {
        FReferenceSkeletonModifier Modifier(Skeleton);
        Modifier.Add(FMeshBoneInfo(TEXT("M4_Root"), TEXT("M4_Root"), INDEX_NONE), FTransform::Identity);
    }

    FAssetRegistryModule::AssetCreated(Skeleton);
    Skeleton->MarkPackageDirty();
    return Skeleton;
#else
    return nullptr;
#endif
}
