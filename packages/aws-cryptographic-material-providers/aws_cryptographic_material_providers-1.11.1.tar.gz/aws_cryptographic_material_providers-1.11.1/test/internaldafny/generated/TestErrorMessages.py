import sys
from typing import Callable, Any, TypeVar, NamedTuple
from math import floor
from itertools import count

import module_ as module_
import _dafny as _dafny
import System_ as System_
import smithy_dafny_standard_library.internaldafny.generated.Wrappers as Wrappers
import smithy_dafny_standard_library.internaldafny.generated.BoundedInts as BoundedInts
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary_UInt as StandardLibrary_UInt
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary_MemoryMath as StandardLibrary_MemoryMath
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary_Sequence as StandardLibrary_Sequence
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary_String as StandardLibrary_String
import smithy_dafny_standard_library.internaldafny.generated.StandardLibrary as StandardLibrary
import smithy_dafny_standard_library.internaldafny.generated.UTF8 as UTF8
import aws_cryptography_internal_dynamodb.internaldafny.generated.ComAmazonawsDynamodbTypes as ComAmazonawsDynamodbTypes
import aws_cryptography_internal_kms.internaldafny.generated.ComAmazonawsKmsTypes as ComAmazonawsKmsTypes
import aws_cryptographic_material_providers.internaldafny.generated.AwsCryptographyKeyStoreTypes as AwsCryptographyKeyStoreTypes
import smithy_dafny_standard_library.internaldafny.generated.Relations as Relations
import smithy_dafny_standard_library.internaldafny.generated.Seq_MergeSort as Seq_MergeSort
import smithy_dafny_standard_library.internaldafny.generated.Math as Math
import smithy_dafny_standard_library.internaldafny.generated.Seq as Seq
import smithy_dafny_standard_library.internaldafny.generated.Actions as Actions
import aws_cryptography_primitives.internaldafny.generated.AwsCryptographyPrimitivesTypes as AwsCryptographyPrimitivesTypes
import aws_cryptographic_material_providers.internaldafny.generated.AwsCryptographyMaterialProvidersTypes as AwsCryptographyMaterialProvidersTypes
import aws_cryptographic_material_providers.internaldafny.generated.AwsArnParsing as AwsArnParsing
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsMrkMatchForDecrypt as AwsKmsMrkMatchForDecrypt
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsUtils as AwsKmsUtils
import aws_cryptographic_material_providers.internaldafny.generated.KeyStoreErrorMessages as KeyStoreErrorMessages
import aws_cryptographic_material_providers.internaldafny.generated.KmsArn as KmsArn
import aws_cryptographic_material_providers.internaldafny.generated.Structure as Structure
import aws_cryptographic_material_providers.internaldafny.generated.KMSKeystoreOperations as KMSKeystoreOperations
import aws_cryptographic_material_providers.internaldafny.generated.DDBKeystoreOperations as DDBKeystoreOperations
import aws_cryptographic_material_providers.internaldafny.generated.CreateKeys as CreateKeys
import aws_cryptographic_material_providers.internaldafny.generated.CreateKeyStoreTable as CreateKeyStoreTable
import aws_cryptographic_material_providers.internaldafny.generated.GetKeys as GetKeys
import smithy_dafny_standard_library.internaldafny.generated.UUID as UUID
import smithy_dafny_standard_library.internaldafny.generated.OsLang as OsLang
import smithy_dafny_standard_library.internaldafny.generated.FileIO as FileIO
import smithy_dafny_standard_library.internaldafny.generated.Time as Time
import aws_cryptographic_material_providers.internaldafny.generated.AwsCryptographyKeyStoreOperations as AwsCryptographyKeyStoreOperations
import aws_cryptography_internal_kms.internaldafny.generated.Com_Amazonaws_Kms as Com_Amazonaws_Kms
import aws_cryptography_internal_dynamodb.internaldafny.generated.Com_Amazonaws_Dynamodb as Com_Amazonaws_Dynamodb
import aws_cryptographic_material_providers.internaldafny.generated.KeyStore as KeyStore
import smithy_dafny_standard_library.internaldafny.generated.Base64 as Base64
import aws_cryptographic_material_providers.internaldafny.generated.AlgorithmSuites as AlgorithmSuites
import aws_cryptographic_material_providers.internaldafny.generated.Materials as Materials
import aws_cryptographic_material_providers.internaldafny.generated.Keyring as Keyring
import smithy_dafny_standard_library.internaldafny.generated.SortedSets as SortedSets
import aws_cryptographic_material_providers.internaldafny.generated.CanonicalEncryptionContext as CanonicalEncryptionContext
import aws_cryptography_primitives.internaldafny.generated.ExternRandom as ExternRandom
import aws_cryptography_primitives.internaldafny.generated.Random as Random
import aws_cryptography_primitives.internaldafny.generated.AESEncryption as AESEncryption
import aws_cryptography_primitives.internaldafny.generated.ExternDigest as ExternDigest
import aws_cryptography_primitives.internaldafny.generated.Digest as Digest
import aws_cryptography_primitives.internaldafny.generated.HMAC as HMAC
import aws_cryptography_primitives.internaldafny.generated.WrappedHMAC as WrappedHMAC
import aws_cryptography_primitives.internaldafny.generated.HKDF as HKDF
import aws_cryptography_primitives.internaldafny.generated.WrappedHKDF as WrappedHKDF
import aws_cryptography_primitives.internaldafny.generated.Signature as Signature
import aws_cryptography_primitives.internaldafny.generated.KdfCtr as KdfCtr
import aws_cryptography_primitives.internaldafny.generated.RSAEncryption as RSAEncryption
import aws_cryptography_primitives.internaldafny.generated.ECDH as ECDH
import aws_cryptography_primitives.internaldafny.generated.AwsCryptographyPrimitivesOperations as AwsCryptographyPrimitivesOperations
import aws_cryptography_primitives.internaldafny.generated.AtomicPrimitives as AtomicPrimitives
import aws_cryptographic_material_providers.internaldafny.generated.MaterialWrapping as MaterialWrapping
import aws_cryptographic_material_providers.internaldafny.generated.IntermediateKeyWrapping as IntermediateKeyWrapping
import aws_cryptographic_material_providers.internaldafny.generated.EdkWrapping as EdkWrapping
import aws_cryptographic_material_providers.internaldafny.generated.ErrorMessages as ErrorMessages
import aws_cryptographic_material_providers.internaldafny.generated.RawAESKeyring as RawAESKeyring
import aws_cryptographic_material_providers.internaldafny.generated.Constants as Constants
import aws_cryptographic_material_providers.internaldafny.generated.EcdhEdkWrapping as EcdhEdkWrapping
import aws_cryptographic_material_providers.internaldafny.generated.RawECDHKeyring as RawECDHKeyring
import aws_cryptographic_material_providers.internaldafny.generated.RawRSAKeyring as RawRSAKeyring
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsKeyring as AwsKmsKeyring
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsDiscoveryKeyring as AwsKmsDiscoveryKeyring
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsEcdhKeyring as AwsKmsEcdhKeyring
import smithy_dafny_standard_library.internaldafny.generated.DafnyLibraries as DafnyLibraries
import aws_cryptographic_material_providers.internaldafny.generated.LocalCMC as LocalCMC
import aws_cryptographic_material_providers.internaldafny.generated.SynchronizedLocalCMC as SynchronizedLocalCMC
import aws_cryptographic_material_providers.internaldafny.generated.StormTracker as StormTracker
import aws_cryptographic_material_providers.internaldafny.generated.StormTrackingCMC as StormTrackingCMC
import aws_cryptographic_material_providers.internaldafny.generated.CacheConstants as CacheConstants
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsHierarchicalKeyring as AwsKmsHierarchicalKeyring
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsMrkDiscoveryKeyring as AwsKmsMrkDiscoveryKeyring
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsMrkKeyring as AwsKmsMrkKeyring
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsRsaKeyring as AwsKmsRsaKeyring
import aws_cryptographic_material_providers.internaldafny.generated.MultiKeyring as MultiKeyring
import aws_cryptographic_material_providers.internaldafny.generated.AwsKmsMrkAreUnique as AwsKmsMrkAreUnique
import aws_cryptographic_material_providers.internaldafny.generated.StrictMultiKeyring as StrictMultiKeyring
import aws_cryptographic_material_providers.internaldafny.generated.DiscoveryMultiKeyring as DiscoveryMultiKeyring
import aws_cryptographic_material_providers.internaldafny.generated.MrkAwareDiscoveryMultiKeyring as MrkAwareDiscoveryMultiKeyring
import aws_cryptographic_material_providers.internaldafny.generated.MrkAwareStrictMultiKeyring as MrkAwareStrictMultiKeyring
import aws_cryptographic_material_providers.internaldafny.generated.CMM as CMM
import aws_cryptographic_material_providers.internaldafny.generated.Defaults as Defaults
import aws_cryptographic_material_providers.internaldafny.generated.Commitment as Commitment
import aws_cryptographic_material_providers.internaldafny.generated.DefaultCMM as DefaultCMM
import aws_cryptographic_material_providers.internaldafny.generated.DefaultClientSupplier as DefaultClientSupplier
import aws_cryptographic_material_providers.internaldafny.generated.Utils as Utils
import aws_cryptographic_material_providers.internaldafny.generated.RequiredEncryptionContextCMM as RequiredEncryptionContextCMM
import aws_cryptographic_material_providers.internaldafny.generated.AwsCryptographyMaterialProvidersOperations as AwsCryptographyMaterialProvidersOperations
import aws_cryptographic_material_providers.internaldafny.generated.MaterialProviders as MaterialProviders
import aws_cryptography_primitives.internaldafny.generated.AesKdfCtr as AesKdfCtr
import smithy_dafny_standard_library.internaldafny.generated.Unicode as Unicode
import smithy_dafny_standard_library.internaldafny.generated.Functions as Functions
import smithy_dafny_standard_library.internaldafny.generated.Utf8EncodingForm as Utf8EncodingForm
import smithy_dafny_standard_library.internaldafny.generated.Utf16EncodingForm as Utf16EncodingForm
import smithy_dafny_standard_library.internaldafny.generated.UnicodeStrings as UnicodeStrings
import smithy_dafny_standard_library.internaldafny.generated.GeneralInternals as GeneralInternals
import smithy_dafny_standard_library.internaldafny.generated.MulInternalsNonlinear as MulInternalsNonlinear
import smithy_dafny_standard_library.internaldafny.generated.MulInternals as MulInternals
import smithy_dafny_standard_library.internaldafny.generated.Mul as Mul
import smithy_dafny_standard_library.internaldafny.generated.ModInternalsNonlinear as ModInternalsNonlinear
import smithy_dafny_standard_library.internaldafny.generated.DivInternalsNonlinear as DivInternalsNonlinear
import smithy_dafny_standard_library.internaldafny.generated.ModInternals as ModInternals
import smithy_dafny_standard_library.internaldafny.generated.DivInternals as DivInternals
import smithy_dafny_standard_library.internaldafny.generated.DivMod as DivMod
import smithy_dafny_standard_library.internaldafny.generated.Power as Power
import smithy_dafny_standard_library.internaldafny.generated.Logarithm as Logarithm
import smithy_dafny_standard_library.internaldafny.generated.StandardLibraryInterop as StandardLibraryInterop
import smithy_dafny_standard_library.internaldafny.generated.Streams as Streams
import smithy_dafny_standard_library.internaldafny.generated.Sorting as Sorting
import smithy_dafny_standard_library.internaldafny.generated.HexStrings as HexStrings
import smithy_dafny_standard_library.internaldafny.generated.GetOpt as GetOpt
import smithy_dafny_standard_library.internaldafny.generated.FloatCompare as FloatCompare
import smithy_dafny_standard_library.internaldafny.generated.ConcurrentCall as ConcurrentCall
import smithy_dafny_standard_library.internaldafny.generated.Base64Lemmas as Base64Lemmas
import Fixtures as Fixtures
import CleanupItems as CleanupItems
import TestVersionKey as TestVersionKey
import TestLyingBranchKey as TestLyingBranchKey
import TestGetKeys as TestGetKeys
import TestDiscoveryGetKeys as TestDiscoveryGetKeys
import TestCreateKeysWithSpecialECKeys as TestCreateKeysWithSpecialECKeys
import TestCreateKeys as TestCreateKeys
import TestCreateKeyStore as TestCreateKeyStore
import TestConfig as TestConfig
import TestUtils as TestUtils
import TestIntermediateKeyWrapping as TestIntermediateKeyWrapping

# Module: TestErrorMessages

class default__:
    def  __init__(self):
        pass

    @staticmethod
    def TestIncorrectRawDataKeys():
        d_0_datakey_: _dafny.Seq
        d_0_datakey_ = _dafny.Seq("0")
        d_1_keyringName_: _dafny.Seq
        d_1_keyringName_ = _dafny.Seq("RSAKeyring")
        d_2_keyProviderId_: _dafny.Seq
        d_2_keyProviderId_ = _dafny.Seq("TestProvider")
        d_3_actualErrorMessage_: _dafny.Seq
        d_3_actualErrorMessage_ = ErrorMessages.default__.IncorrectRawDataKeys(d_0_datakey_, d_1_keyringName_, d_2_keyProviderId_)
        d_4_ExpectErrorMessage_: _dafny.Seq
        d_4_ExpectErrorMessage_ = _dafny.Seq("EncryptedDataKey 0 did not match RSAKeyring. Expected: keyProviderId: TestProvider.\n")
        if not((d_3_actualErrorMessage_) == (d_4_ExpectErrorMessage_)):
            raise _dafny.HaltException("dafny/AwsCryptographicMaterialProviders/test/TestErrorMessages.dfy(22,4): " + _dafny.string_of(_dafny.Seq("expectation violation")))

    @staticmethod
    def TestIncorrectDataKeys():
        d_0_dummyKey_: _dafny.Seq
        d_0_dummyKey_ = _dafny.Seq([AwsCryptographyMaterialProvidersTypes.EncryptedDataKey_EncryptedDataKey(default__.awskms, default__.keyproviderInfoA, _dafny.Seq([1, 2, 3, 4, 5])), AwsCryptographyMaterialProvidersTypes.EncryptedDataKey_EncryptedDataKey(default__.awskmsrsa, default__.keyproviderInfoB, _dafny.Seq([1, 2, 3, 4, 5])), AwsCryptographyMaterialProvidersTypes.EncryptedDataKey_EncryptedDataKey(default__.awskmshierarchy, default__.keyproviderInfoC, _dafny.Seq([64, 92, 115, 7, 85, 121, 112, 79, 69, 12, 82, 25, 67, 34, 11, 66, 93, 45, 40, 23, 90, 61, 16, 28, 59, 114, 52, 122, 50, 23, 11, 101, 48, 53, 30, 120, 51, 74, 77, 53, 57, 99, 53, 13, 30, 21, 109, 85, 15, 86, 47, 84, 91, 85, 87, 60, 4, 56, 67, 74, 29, 87, 85, 106, 8, 82, 63, 114, 100, 110, 68, 58, 83, 24, 111, 41, 21, 91, 122, 61, 118, 37, 72, 38, 67, 2, 17, 61, 17, 121, 7, 90, 117, 49, 30, 20, 89, 68, 33, 111, 107, 5, 120, 20, 95, 78, 70, 2, 49, 84, 39, 50, 40, 40, 115, 114, 76, 18, 103, 84, 34, 123, 1, 125, 61, 33, 13, 18, 81, 24, 53, 53, 26, 60, 52, 85, 81, 96, 85, 72]))])
        d_1_valueOrError0_: Wrappers.Result = Wrappers.Result.default(_dafny.Seq)()
        d_1_valueOrError0_ = ErrorMessages.default__.IncorrectDataKeys(d_0_dummyKey_, AlgorithmSuites.default__.GetSuite(default__.TEST__DBE__ALG__SUITE__ID), _dafny.Seq(""))
        if not(not((d_1_valueOrError0_).IsFailure())):
            raise _dafny.HaltException("dafny/AwsCryptographicMaterialProviders/test/TestErrorMessages.dfy(82,30): " + _dafny.string_of(d_1_valueOrError0_))
        d_2_actualErrorMessage_: _dafny.Seq
        d_2_actualErrorMessage_ = (d_1_valueOrError0_).Extract()
        d_3_ExpectErrorMessage_: _dafny.Seq
        d_3_ExpectErrorMessage_ = (((_dafny.Seq("Unable to decrypt data key: No Encrypted Data Keys found to match. \n Expected: \n")) + (_dafny.Seq("KeyProviderId: aws-kms, KeyProviderInfo: keyproviderInfoA\n"))) + (_dafny.Seq("KeyProviderId: aws-kms-rsa, KeyProviderInfo: keyproviderInfoB\n"))) + (_dafny.Seq("KeyProviderId: aws-kms-hierarchy, KeyProviderInfo: keyproviderInfoC, BranchKeyVersion: 155b7a3d-7625-4826-4302-113d1179075a\n"))
        if not((d_2_actualErrorMessage_) == (d_3_ExpectErrorMessage_)):
            raise _dafny.HaltException("dafny/AwsCryptographicMaterialProviders/test/TestErrorMessages.dfy(87,4): " + _dafny.string_of(_dafny.Seq("expectation violation")))

    @_dafny.classproperty
    def awskms(instance):
        d_0_s_ = _dafny.Seq([97, 119, 115, 45, 107, 109, 115])
        return d_0_s_
    @_dafny.classproperty
    def keyproviderInfoA(instance):
        d_0_s_ = _dafny.Seq([107, 101, 121, 112, 114, 111, 118, 105, 100, 101, 114, 73, 110, 102, 111, 65])
        return d_0_s_
    @_dafny.classproperty
    def awskmsrsa(instance):
        d_0_s_ = _dafny.Seq([97, 119, 115, 45, 107, 109, 115, 45, 114, 115, 97])
        return d_0_s_
    @_dafny.classproperty
    def keyproviderInfoB(instance):
        d_0_s_ = _dafny.Seq([107, 101, 121, 112, 114, 111, 118, 105, 100, 101, 114, 73, 110, 102, 111, 66])
        return d_0_s_
    @_dafny.classproperty
    def awskmshierarchy(instance):
        d_0_s_ = _dafny.Seq([97, 119, 115, 45, 107, 109, 115, 45, 104, 105, 101, 114, 97, 114, 99, 104, 121])
        return d_0_s_
    @_dafny.classproperty
    def keyproviderInfoC(instance):
        d_0_s_ = _dafny.Seq([107, 101, 121, 112, 114, 111, 118, 105, 100, 101, 114, 73, 110, 102, 111, 67])
        return d_0_s_
    @_dafny.classproperty
    def TEST__DBE__ALG__SUITE__ID(instance):
        return AwsCryptographyMaterialProvidersTypes.AlgorithmSuiteId_DBE(AwsCryptographyMaterialProvidersTypes.DBEAlgorithmSuiteId_ALG__AES__256__GCM__HKDF__SHA512__COMMIT__KEY__SYMSIG__HMAC__SHA384())
