#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LiveLinkTypes.h"
#include "M4RadialMouthPOCActor.generated.h"

class UPoseableMeshComponent;
class USkeletalMesh;

/** Minimal M4 actuator test: a single normalized value moves 12 radial bones. */
UCLASS()
class PERFBRIDGEMH_API AM4RadialMouthPOCActor : public AActor
{
    GENERATED_BODY()

public:
    AM4RadialMouthPOCActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "M4")
    TObjectPtr<UPoseableMeshComponent> MouthMesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "M4", meta = (ClampMin = "0.0", ClampMax = "1.0", UIMin = "0.0", UIMax = "1.0"))
    float M4_Aperture = 0.5f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "M4")
    bool bAutoOscillate = true;

    /** When enabled, a Live Link Face Basic Role subject's jawOpen curve drives the actuator. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "M4|Live Link")
    bool bUseLiveLink = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "M4|Live Link")
    FLiveLinkSubjectName LiveLinkSubject;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "M4|Live Link")
    FName LiveLinkApertureCurve = TEXT("jawOpen");

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Transient, Category = "M4|Live Link")
    bool bLiveLinkFrameValid = false;

    /** Explains whether the selected subject and aperture curve are being received. */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Transient, Category = "M4|Live Link")
    FString LiveLinkStatus = TEXT("Waiting for Play");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "M4", meta = (ClampMin = "0.01"))
    float OscillationSpeed = 2.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "M4", meta = (ClampMin = "0.01"))
    float MinRadialScale = 0.65f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "M4", meta = (ClampMin = "0.01"))
    float MaxRadialScale = 1.35f;

    UFUNCTION(BlueprintCallable, Category = "M4")
    void ApplyAperture(float Value);

    /** Also accepts a synthetic curve map, so the adapter can be tested without capture hardware. */
    UFUNCTION(BlueprintCallable, Category = "M4|Live Link")
    bool ApplyLiveLinkCurves(const TMap<FName, float>& Curves);

    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void Tick(float DeltaSeconds) override;

private:
    FTransform GetRestComponentTransform(const USkeletalMesh* Mesh, int32 BoneIndex) const;
    bool PollLiveLink();
    float ElapsedTime = 0.0f;
};
