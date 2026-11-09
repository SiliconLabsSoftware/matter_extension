#ifndef SLI_PSA_BUILTIN_CONFIG_H
#define SLI_PSA_BUILTIN_CONFIG_H

// Included as TF_PSA_CRYPTO_USER_CONFIG_FILE, after psa_crypto_config.h
// and before TF-PSA-Crypto enables software builtins. Drop the accelerated
// AES mechanisms so the PSA driver is used. crypto_adjust restores a builtin
// when the device does not accelerate that mechanism.

#undef MBEDTLS_PSA_BUILTIN_KEY_TYPE_AES
#undef MBEDTLS_PSA_BUILTIN_ALG_ECB_NO_PADDING
#undef MBEDTLS_PSA_BUILTIN_ALG_CMAC


#endif // SLI_PSA_BUILTIN_CONFIG_H
