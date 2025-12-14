import sys
from utils import load_json_db, clean_string, get_tokens, safe_print, PYPY_URL, WD_URL

def main():
    # Parse args
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Check if arg is a file
        if arg.endswith('.txt') or arg.endswith('.json'):
            try:
                with open(arg, 'r', encoding='utf-8') as f:
                    input_str = f.read().strip()
            except Exception as e:
                print(f"Error reading input file: {e}")
                return
        else:
            input_str = arg
    else:
        print("Usage: python convert_pypy_to_wd.py <ids_separated_by_comma_or_file>")
        print("Example: python convert_pypy_to_wd.py 2330,3429,3605")
        return

    wd_data = load_json_db('wannadance.json', WD_URL)
    pypy_data = load_json_db('pypydance.json', PYPY_URL)

    # Build Pypy Map
    pypy_songs = {}
    if 'songs' in pypy_data:
        for song in pypy_data['songs']:
            pypy_songs[song['i']] = {
                'name': song.get('n', ''),
                'clean_name': clean_string(song.get('n', ''))
            }

    # Build WD List
    wd_songs = []
    if 'groups' in wd_data and 'contents' in wd_data['groups']:
        for group in wd_data['groups']['contents']:
            if 'songInfos' in group:
                for song in group['songInfos']:
                    name = song.get('name', '')
                    artist = song.get('artist', '')
                    wd_songs.append({
                        'id': song['id'],
                        'name': name,
                        'artist': artist,
                        'clean_name': clean_string(name),
                        'clean_artist': clean_string(artist)
                    })

    # Clean input string
    # Remove any potential headers if user pastes full export string? 
    # Pypy format is just numbers usually, but let's be safe.
    input_ids = [int(x.strip()) for x in input_str.split(',') if x.strip().isdigit()]
    
    output_ids = []
    
    print("\nStarting conversion (PypyDance -> WannaDance)...")
    safe_print(f"{'Pypy ID':<8} | {'Status':<10} | {'Pypy Name':<30} | {'WD Match'}")
    print("-" * 100)

    for pypy_id in input_ids:
        if pypy_id not in pypy_songs:
            safe_print(f"{pypy_id:<8} | {'MISSING':<10} | {'N/A':<30} | ID not found in pypydance.json")
            continue

        pypy_entry = pypy_songs[pypy_id]
        pypy_name_raw = pypy_entry['name']
        pypy_name_clean = pypy_entry['clean_name']
        pypy_name_tokens = get_tokens(pypy_name_clean)

        # Skip empty names
        if not pypy_name_clean:
             safe_print(f"{pypy_id:<8} | {'SKIPPED':<10} | {'(Empty Name)':<30} | Cannot match empty name")
             continue

        candidates = []
        for wd_song in wd_songs:
            wd_name_clean = wd_song['clean_name']
            wd_artist_clean = wd_song['clean_artist']
            wd_name_tokens = get_tokens(wd_name_clean)
            wd_artist_tokens = get_tokens(wd_artist_clean)
            
            score = 0
            
            # Reverse matching logic: Pypy (Source) -> WD (Target)
            # Pypy often has Artist info in 'name', WD splits it.
            
            # 1. Token Overlap (WD Name in Pypy Name) - Weight 60
            if wd_name_tokens:
                intersection = wd_name_tokens.intersection(pypy_name_tokens)
                overlap_ratio = len(intersection) / len(wd_name_tokens)
                score += overlap_ratio * 60
            
            # 2. Artist Match (WD Artist in Pypy Name) - Weight 40
            if wd_artist_tokens:
                artist_intersection = wd_artist_tokens.intersection(pypy_name_tokens)
                artist_overlap_ratio = len(artist_intersection) / len(wd_artist_tokens)
                score += artist_overlap_ratio * 40
            
            # 3. Exact Substring Boost
            if wd_name_clean and wd_name_clean in pypy_name_clean:
                score += 20
            
            if score > 0:
                candidates.append((score, wd_song))

        # Sort candidates by score desc
        candidates.sort(key=lambda x: x[0], reverse=True)

        if not candidates:
             safe_print(f"{pypy_id:<8} | {'NO MATCH':<10} | {pypy_name_raw[:30]:<30} | No candidates found")
        else:
            best_score, best_match = candidates[0]
            # Threshold
            threshold = 40 
            if best_score >= threshold: 
                output_ids.append(str(best_match['id']))
                safe_print(f"{pypy_id:<8} | {'MATCH':<10} | {pypy_name_raw[:30]:<30} | [{best_match['id']}] {best_match['name']} (Score: {best_score:.1f})")
            else:
                 safe_print(f"{pypy_id:<8} | {'LOW SCORE':<10} | {pypy_name_raw[:30]:<30} | Best: [{best_match['id']}] {best_match['name']} (Score: {best_score:.1f})")

    safe_print("\n" + "="*50)
    safe_print("Conversion Result (WannaDance format):")
    result_str = "WannaFavorite:" + ",".join(output_ids)
    safe_print(result_str)
    
    # Save to file
    with open('converted_wd_list.txt', 'w', encoding='utf-8') as f:
        f.write(result_str)
    print("Saved to converted_wd_list.txt")

if __name__ == "__main__":
    main()

