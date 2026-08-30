#!/usr/bin/env python3
"""Publish the 2.4.1 sync and support documentation without claiming release."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MARKER = "data-release-docs=\"2.4.1\""

ENGLISH = {
    "support": (
        '<section class="doc-content" data-release-docs="2.4.1">'
        '<p class="doc-meta">Record Picker 2.4.1</p>'
        '<h2>Encrypted cross-platform sync</h2>'
        '<p>On the device whose collection is current, open <strong>Settings → Sync → '
        'Cross-platform sync</strong>, create a shared library and save its single '
        '<code>.recordpickersync</code> package in a dedicated OneDrive or other shared '
        'folder. Keep the association code private.</p>'
        '<p>On another device, enter that code and choose the same package. In the iOS '
        'Files interface the confirmation button can read <strong>Save</strong>: Record '
        'Picker is granting the package permission, not creating a readable copy of your '
        'collection. Do not create several libraries in the same folder.</p>'
        '<p>Snapshots, changes and artwork are encrypted and authenticated on the device. '
        'If the provider was offline, let it finish transferring the package, return to '
        'Record Picker and choose <strong>Synchronize now</strong>. A separate verified '
        '<code>.recordpicker</code> backup remains the safest independent recovery copy.</p>'
        '<h2>2.4.1 reliability fixes</h2>'
        '<p>The update stabilises manual entry focus on iPhone, improves MusicBrainz '
        'fallback searches and error messages, makes Notes easier to find, restores the '
        'Sync Centre on iPhone and iPad, and keeps secondary Mac windows independently '
        'resizable.</p></section>'
    ),
    "privacy": (
        '<section class="doc-content" data-release-docs="2.4.1">'
        '<p class="doc-meta">Cross-platform synchronisation</p>'
        '<h2>Optional encrypted shared folder</h2>'
        '<p>If you enable cross-platform synchronisation, you choose a folder made '
        'available by Files or Finder, for example through OneDrive. Record Picker does '
        'not require or operate a user account for this feature. Collection snapshots, '
        'incremental changes and artwork are encrypted and authenticated on your device '
        'before they are written to that folder.</p>'
        '<p>The folder provider stores encrypted files and may receive ordinary account, '
        'transfer and network metadata. The association key is kept in the secure '
        'credential store of each associated device and is not uploaded separately. '
        'Record Picker’s developer receives neither the folder nor a browsable copy of '
        'the collection.</p>'
        '<p>You can disconnect one device without deleting the shared folder. Losing the '
        'association key on every device makes the encrypted package unreadable. The '
        'separate <code>.recordpicker</code> backup format remains available independently.'
        '</p></section>'
    ),
}

FRENCH = {
    "support": (
        '<section class="doc-content" data-release-docs="2.4.1">'
        '<p class="doc-meta">Record Picker 2.4.1</p>'
        '<h2>Synchronisation multiplateforme chiffrée</h2>'
        '<p>Sur l’appareil dont la collection est à jour, ouvrez <strong>Réglages → '
        'Synchronisation → Synchronisation multiplateforme</strong>, créez une bibliothèque '
        'partagée et enregistrez son unique paquet <code>.recordpickersync</code> dans un '
        'dossier OneDrive dédié ou un autre dossier partagé. Conservez le code '
        'd’association de façon confidentielle.</p>'
        '<p>Sur l’autre appareil, saisissez ce code et choisissez le même paquet. Dans '
        'l’interface Fichiers d’iOS, le bouton de confirmation peut s’intituler '
        '<strong>Enregistrer</strong> : Record Picker accorde l’accès au paquet, sans créer '
        'une copie lisible de la collection. Ne créez pas plusieurs bibliothèques dans le '
        'même dossier.</p>'
        '<p>Les instantanés, modifications et pochettes sont chiffrés et authentifiés sur '
        'l’appareil. Si le fournisseur était hors ligne, laissez-le terminer le transfert, '
        'revenez dans Record Picker puis choisissez <strong>Synchroniser maintenant</strong>. '
        'Une sauvegarde <code>.recordpicker</code> vérifiée reste la meilleure copie de '
        'secours indépendante.</p>'
        '<h2>Correctifs de fiabilité 2.4.1</h2>'
        '<p>La mise à jour stabilise le champ actif pendant la saisie manuelle sur iPhone, '
        'améliore les recherches de secours et les messages MusicBrainz, rend Notes plus '
        'visible, rétablit le centre de synchronisation sur iPhone et iPad et conserve des '
        'fenêtres secondaires Mac redimensionnables indépendamment.</p></section>'
    ),
    "privacy": (
        '<section class="doc-content" data-release-docs="2.4.1">'
        '<p class="doc-meta">Synchronisation multiplateforme</p>'
        '<h2>Dossier partagé chiffré facultatif</h2>'
        '<p>Si vous activez la synchronisation multiplateforme, vous choisissez un dossier '
        'accessible dans Fichiers ou le Finder, par exemple via OneDrive. Record Picker '
        'n’exige et n’exploite aucun compte utilisateur pour cette fonction. Les '
        'instantanés de collection, modifications et pochettes sont chiffrés et authentifiés '
        'sur votre appareil avant leur écriture dans ce dossier.</p>'
        '<p>Le fournisseur du dossier stocke des fichiers chiffrés et peut recevoir les '
        'métadonnées ordinaires de compte, de transfert et de réseau. La clé d’association '
        'reste dans le trousseau sécurisé de chaque appareil associé et n’est pas téléversée '
        'séparément. Le développeur de Record Picker ne reçoit ni le dossier ni une copie '
        'consultable de la collection.</p>'
        '<p>Vous pouvez déconnecter un appareil sans supprimer le dossier partagé. La perte '
        'de la clé sur tous les appareils rend le paquet chiffré illisible. Le format de '
        'sauvegarde distinct <code>.recordpicker</code> reste disponible indépendamment.'
        '</p></section>'
    ),
}


def update_page(path: Path, block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    marker = "</main>"
    if marker not in text:
        raise RuntimeError(f"Missing main element in {path}")
    path.write_text(text.replace(marker, block + marker, 1), encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for directory in ("", "en-au", "en-ca", "en-gb", "en-us"):
        base = ROOT / directory if directory else ROOT
        changed += update_page(base / "support" / "index.html", ENGLISH["support"])
        changed += update_page(base / "privacy" / "index.html", ENGLISH["privacy"])
    for directory in ("fr", "fr-ca"):
        base = ROOT / directory
        changed += update_page(base / "support" / "index.html", FRENCH["support"])
        changed += update_page(base / "privacy" / "index.html", FRENCH["privacy"])
    print(f"Prepared 2.4.1 documentation in {changed} page(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
