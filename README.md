# GPG Vault

Simple GPG based file encryption utility.

Allows viewing and editing of encrypted files with passphrase caching.

## Installing 

Using PIP:
```
% pip install gpg-vault
```

## Viewing files

```
% vcat file.txt.gpg 
Passphrase: ************
Hello

[Use CMD-K to clear sensitve information from the screen]
%
% vcat file.txt.gpg 
Hello

[Use CMD-K to clear sensitve information from the screen]
%
```

## Editing files

```
% vedit file.txt
Passphrase: ************ 
[wiping file file.txt.gpg]
[encrypting file /tmp/v/37795/37795 to file.txt.gpg]
[wiping directory/tmp/v/37795]
%
% vcat file.txt.gpg 
Hello

[Use CMD-K to clear sensitve information from the screen]
%
```

## Encrypting files

```
% vencrypt file.txt 
Passphrase: ************ 
Confirm Passphrase: ************ 
[encrypting file file.txt to file.txt.gpg]
[wiping file file.txt]
```

## Clearing cached passphrases

```
% vclear
```
