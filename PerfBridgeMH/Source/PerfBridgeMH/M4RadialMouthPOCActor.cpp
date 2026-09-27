#include "M4RadialMouthPOCActor.h"

#include "Animation/Skeleton.h"
#include "Components/PoseableMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Features/IModularFeatures.h"
#include "ILiveLinkClient.h"
#include "Roles/LiveLinkBasicRole.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

AM4RadialMouthPOCActor::AM4RadialMouthPOCActor()
{
    PrimaryActorTick.bCanEverTick = true;
    MouthMesh = CreateDefaultSubobject<UPoseableMeshComponent>(TEXT("MouthMesh"));
    RootComponent = MouthMesh;
    MouthMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

    static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(
        TEXT("/Game/PlanetAnimora/POC/M4/SK_M4_RadialMouth.SK_M4_RadialMouth"));
    if (MeshAsset.Succeeded())
    {
        MouthMesh->SetSkinnedAssetAndUpdate(MeshAsset.Object);
    }
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> DebugMaterial(
        TEXT("/Engine/EngineMaterials/DefaultMaterial.DefaultMaterial"));
    if (DebugMaterial.Succeeded())
    {
        MouthMesh->SetMaterial(0, DebugMaterial.Object);
    }
}

FTransform AM4RadialMouthPOCActor::GetRestComponentTransform(const USkeletalMesh* Mesh, int32 BoneIndex) const
{
    const FReferenceSkeleton& Ref = Mesh->GetRefSkeleton();
    FTransform Result = FTransform::Identity;
    while (BoneIndex != INDEX_NONE)
    {
        Result = Result * Ref.GetRefBonePose()[BoneIndex];
        BoneIndex = Ref.GetParentIndex(BoneIndex);
    }
    return Result;
}

void AM4RadialMouthPOCActor::ApplyAperture(float Value)
{
    if (!MouthMesh || !MouthMesh->GetSkinnedAsset())
    {
        return;
    }

    M4_Aperture = FMath::Clamp(Value, 0.0f, 1.0f);
    const float RadialScale = FMath::Lerp(MinRadialScale, MaxRadialScale, M4_Aperture);
    const USkeletalMesh* Mesh = Cast<USkeletalMesh>(MouthMesh->GetSkinnedAsset());
    if (!Mesh)
    {
        return;
    }
    const FReferenceSkeleton& Ref = Mesh->GetRefSkeleton();
    const int32 CenterIndex = Ref.FindBoneIndex(TEXT("M4_MouthCenter"));
    if (CenterIndex == INDEX_NONE)
    {
        return;
    }
    const FVector Center = GetRestComponentTransform(Mesh, CenterIndex).GetLocation();

    for (int32 Index = 0; Index < 12; ++Index)
    {
        const FName BoneName(*FString::Printf(TEXT("M4_Radial_%02d"), Index));
        const int32 BoneIndex = Ref.FindBoneIndex(BoneName);
        if (BoneIndex == INDEX_NONE)
        {
            continue;
        }
        FTransform BoneTransform = GetRestComponentTransform(Mesh, BoneIndex);
        BoneTransform.SetLocation(Center + (BoneTransform.GetLocation() - Center) * RadialScale);
        MouthMesh->SetBoneTransformByName(BoneName, BoneTransform, EBoneSpaces::ComponentSpace);
    }
    MouthMesh->RefreshBoneTransforms();
}

void AM4RadialMouthPOCActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    ApplyAperture(M4_Aperture);
}

bool AM4RadialMouthPOCActor::ApplyLiveLinkCurves(const TMap<FName, float>& Curves)
{
    const float* JawOpen = Curves.Find(LiveLinkApertureCurve);
    if (!JawOpen || !FMath::IsFinite(*JawOpen))
    {
        return false;
    }
    ApplyAperture(*JawOpen);
    return true;
}

bool AM4RadialMouthPOCActor::PollLiveLink()
{
    if (LiveLinkSubject.Name.IsNone())
    {
        LiveLinkStatus = TEXT("Select a Live Link subject");
        return false;
    }
    if (!IModularFeatures::Get().IsModularFeatureAvailable(ILiveLinkClient::ModularFeatureName))
    {
        LiveLinkStatus = TEXT("Live Link client unavailable");
        return false;
    }

    ILiveLinkClient& Client = IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(
        ILiveLinkClient::ModularFeatureName);
    FLiveLinkSubjectFrameData Frame;
    if (!Client.EvaluateFrame_AnyThread(LiveLinkSubject, ULiveLinkBasicRole::StaticClass(), Frame))
    {
        LiveLinkStatus = FString::Printf(TEXT("No Basic-role frame for %s"), *LiveLinkSubject.Name.ToString());
        return false;
    }

    const FLiveLinkBaseStaticData* StaticData = Frame.StaticData.Cast<FLiveLinkBaseStaticData>();
    const FLiveLinkBaseFrameData* FrameData = Frame.FrameData.Cast<FLiveLinkBaseFrameData>();
    if (!StaticData || !FrameData)
    {
        LiveLinkStatus = TEXT("Frame has no curve data");
        return false;
    }

    float CurveValue = 0.0f;
    FName MatchedCurve = LiveLinkApertureCurve;
    bool bFound = StaticData->FindPropertyValue(*FrameData, MatchedCurve, CurveValue);

    // MetaHuman Animator versions may namespace the same control curve.
    if (!bFound && LiveLinkApertureCurve == TEXT("jawOpen"))
    {
        for (const FName& PropertyName : StaticData->PropertyNames)
        {
            if (PropertyName.ToString().EndsWith(TEXT("jawOpen"), ESearchCase::IgnoreCase))
            {
                if (StaticData->FindPropertyValue(*FrameData, PropertyName, CurveValue))
                {
                    MatchedCurve = PropertyName;
                    bFound = true;
                    break;
                }
            }
        }
    }

    if (!bFound)
    {
        FString JawProperties;
        for (const FName& PropertyName : StaticData->PropertyNames)
        {
            const FString Name = PropertyName.ToString();
            if (Name.Contains(TEXT("jaw"), ESearchCase::IgnoreCase))
            {
                if (!JawProperties.IsEmpty()) JawProperties += TEXT(", ");
                JawProperties += Name;
                if (JawProperties.Len() > 180) break;
            }
        }
        LiveLinkStatus = FString::Printf(TEXT("Curve %s missing. Jaw curves: %s"),
            *LiveLinkApertureCurve.ToString(), JawProperties.IsEmpty() ? TEXT("none") : *JawProperties);
        return false;
    }
    if (!FMath::IsFinite(CurveValue))
    {
        LiveLinkStatus = FString::Printf(TEXT("Curve %s is not finite"), *MatchedCurve.ToString());
        return false;
    }

    ApplyAperture(CurveValue);
    LiveLinkStatus = FString::Printf(TEXT("%s = %.3f"), *MatchedCurve.ToString(), CurveValue);
    return true;
}

void AM4RadialMouthPOCActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (bUseLiveLink)
    {
        bLiveLinkFrameValid = PollLiveLink();
        return;
    }
    bLiveLinkFrameValid = false;
    LiveLinkStatus = bAutoOscillate ? TEXT("Sine-wave demo") : TEXT("Manual aperture");
    if (bAutoOscillate)
    {
        ElapsedTime += DeltaSeconds;
        ApplyAperture(0.5f + 0.5f * FMath::Sin(ElapsedTime * OscillationSpeed));
    }
}
