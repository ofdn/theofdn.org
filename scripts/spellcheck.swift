// Spelling and grammar check with the macOS en_GB dictionary.
// Reads JSON [{"file": ..., "text": ...}] on stdin, writes JSON findings to stdout.
// Called by spellcheck.py; not meant to be run on its own.
import AppKit

struct Doc: Codable { let file: String; let text: String }
struct Finding: Codable {
    let file: String; let kind: String; let text: String
    let suggestions: [String]; let context: String
}

let lang = "en_GB"
let checker = NSSpellChecker.shared
_ = checker.setLanguage(lang)
let docs = try JSONDecoder().decode([Doc].self, from: FileHandle.standardInput.readDataToEndOfFile())
var out: [Finding] = []

func context(_ s: NSString, _ r: NSRange) -> String {
    let start = max(0, r.location - 40)
    let end = min(s.length, r.location + r.length + 40)
    return s.substring(with: NSRange(location: start, length: end - start))
        .replacingOccurrences(of: "\n", with: " ")
}

for doc in docs {
    let s = doc.text as NSString
    var pos = 0
    while pos < s.length {
        let r = checker.checkSpelling(of: doc.text, startingAt: pos, language: lang,
                                      wrap: false, inSpellDocumentWithTag: 0, wordCount: nil)
        if r.location == NSNotFound || r.length == 0 { break }
        let guesses = checker.guesses(forWordRange: r, in: doc.text, language: lang,
                                      inSpellDocumentWithTag: 0) ?? []
        out.append(Finding(file: doc.file, kind: "spelling", text: s.substring(with: r),
                           suggestions: Array(guesses.prefix(3)), context: context(s, r)))
        pos = r.location + r.length
    }
    pos = 0
    while pos < s.length {
        var details: NSArray?
        let r = checker.checkGrammar(of: doc.text, startingAt: pos, language: lang,
                                     wrap: false, inSpellDocumentWithTag: 0, details: &details)
        if r.location == NSNotFound || r.length == 0 { break }
        for case let d as [String: Any] in (details as? [Any]) ?? [] {
            let dr = (d[NSGrammarRange] as? NSValue)?.rangeValue ?? NSRange(location: 0, length: 0)
            let abs = NSRange(location: r.location + dr.location, length: dr.length)
            guard abs.location + abs.length <= s.length else { continue }
            out.append(Finding(file: doc.file, kind: "grammar",
                               text: s.substring(with: abs),
                               suggestions: (d[NSGrammarCorrections] as? [String]) ?? [],
                               context: (d[NSGrammarUserDescription] as? String) ?? context(s, abs)))
        }
        pos = r.location + r.length
    }
}
FileHandle.standardOutput.write(try JSONEncoder().encode(out))
