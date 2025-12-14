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
        print("Usage: python convert_wd_to_pypy.py <ids_separated_by_comma_or_file>")
        print("Example: python convert_wd_to_pypy.py 3302,2929,4950")
        return

    wd_data = load_json_db('wannadance.json', WD_URL)
    pypy_data = load_json_db('pypydance.json', PYPY_URL)

    # Build WD Map
    wd_songs = {}
    if 'groups' in wd_data and 'contents' in wd_data['groups']:
        for group in wd_data['groups']['contents']:
            if 'songInfos' in group:
                for song in group['songInfos']:
                    wd_songs[song['id']] = {
                        'name': song.get('name', ''),
                        'artist': song.get('artist', '')
                    }

    # Build Pypy List
    pypy_songs = []
    if 'songs' in pypy_data:
        for song in pypy_data['songs']:
            pypy_songs.append({
                'id': song.get('i'),
                'name': song.get('n', ''),
                'clean_name': clean_string(song.get('n', ''))
            })

    # Clean input string
    input_str = input_str.replace('WannaFavorite:', '').strip()
    input_ids = [int(x.strip()) for x in input_str.split(',') if x.strip().isdigit()]
    
    output_ids = []
    
    print("\nStarting conversion (WannaDance -> PypyDance)...")
    safe_print(f"{'WD ID':<8} | {'Status':<10} | {'WD Name':<30} | {'Pypy Match'}")
    print("-" * 100)

    for wd_id in input_ids:
        if wd_id not in wd_songs:
            safe_print(f"{wd_id:<8} | {'MISSING':<10} | {'N/A':<30} | ID not found in wannadance.json")
            continue

        wd_entry = wd_songs[wd_id]
        wd_name_raw = wd_entry['name']
        wd_artist_raw = wd_entry['artist']
        
        wd_name_clean = clean_string(wd_name_raw)
        wd_artist_clean = clean_string(wd_artist_raw)
        wd_name_tokens = get_tokens(wd_name_clean)
        wd_artist_tokens = get_tokens(wd_artist_clean)

        # Skip empty names
        if not wd_name_clean and not wd_artist_clean:
             safe_print(f"{wd_id:<8} | {'SKIPPED':<10} | {'(Empty Name)':<30} | Cannot match empty name")
             continue

        candidates = []
        for p_song in pypy_songs:
            p_name_clean = p_song['clean_name']
            p_name_tokens = get_tokens(p_name_clean)
            
            score = 0
            
            # 1. Token Overlap (Name) - Weight 60
            if wd_name_tokens:
                intersection = wd_name_tokens.intersection(p_name_tokens)
                overlap_ratio = len(intersection) / len(wd_name_tokens)
                score += overlap_ratio * 60
            
            # 2. Artist Match (Token Overlap) - Weight 40
            if wd_artist_tokens:
                artist_intersection = wd_artist_tokens.intersection(p_name_tokens)
                artist_overlap_ratio = len(artist_intersection) / len(wd_artist_tokens)
                score += artist_overlap_ratio * 40
            
            # 3. Exact Substring Boost - Weight 20
            if wd_name_clean and wd_name_clean in p_name_clean:
                score += 20
            
            if score > 0:
                candidates.append((score, p_song))

        # Sort candidates by score desc
        candidates.sort(key=lambda x: x[0], reverse=True)

        if not candidates:
             safe_print(f"{wd_id:<8} | {'NO MATCH':<10} | {wd_name_raw[:30]:<30} | No candidates found")
        else:
            best_score, best_match = candidates[0]
            # Threshold adjusted for new scoring
            threshold = 40 
            if best_score >= threshold: 
                output_ids.append(str(best_match['id']))
                safe_print(f"{wd_id:<8} | {'MATCH':<10} | {wd_name_raw[:30]:<30} | [{best_match['id']}] {best_match['name']} (Score: {best_score:.1f})")
            else:
                 safe_print(f"{wd_id:<8} | {'LOW SCORE':<10} | {wd_name_raw[:30]:<30} | Best: [{best_match['id']}] {best_match['name']} (Score: {best_score:.1f})")

    safe_print("\n" + "="*50)
    safe_print("Conversion Result (Pypy format):")
    result_str = ",".join(output_ids)
    safe_print(result_str)
    
    # Save to file
    with open('converted_pypy_list.txt', 'w', encoding='utf-8') as f:
        f.write(result_str)
    print("Saved to converted_pypy_list.txt")

if __name__ == "__main__":
    main()
