def chunk_text(text, chunk_size=700, overlap=100):

    # Clean unnecessary whitespace
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    chunks = []

    current_chunk = ""
    
    for line in lines:

        # Add the next line
        potential_chunk = (
            current_chunk + "\n" + line
        ).strip()


        # If the chunk is still within the limit
        if len(potential_chunk) <= chunk_size:

            current_chunk = potential_chunk

        else:

            # Save the current chunk
            if current_chunk:
                chunks.append(current_chunk)

            # Start a new chunk
            current_chunk = line


    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk)


    return chunks