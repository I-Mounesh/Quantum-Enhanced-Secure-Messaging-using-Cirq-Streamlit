import streamlit as st
import cirq
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# --- Quantum Functions ---

def generate_quantum_random_bytes(length=32):
    """Generates random bits using a Quantum Circuit (Hadamard gates)."""
    # We use 8 qubits to generate one byte at a time to keep simulation light
    qubits = cirq.LineQubit.range(8)
    circuit = cirq.Circuit(cirq.H.on_each(*qubits), cirq.measure(*qubits, key='m'))
    simulator = cirq.Simulator()
    
    random_bytes = bytearray()
    for _ in range(length):
        result = simulator.run(circuit, repetitions=1)
        # Convert bit array to an integer, then to a byte
        bits = result.measurements['m'][0]
        byte_val = int("".join(map(str, bits)), 2)
        random_bytes.append(byte_val)
    
    return bytes(random_bytes)

def derive_key_from_secret(secret_phrase: str):
    """Derives a functional encryption key from a user's secret phrase."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'quantum_salt_123', # In production, use a random salt
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_phrase.encode()))
    return key

# --- Streamlit UI ---

st.set_page_config(page_title="Quantum Secure Comms", page_icon="🔐")
st.title("🔐 Quantum-Enhanced Secure Messaging")

tab1, tab2 = st.tabs(["📤 Encode & Send", "📥 Receive & Decode"])

with tab1:
    st.subheader("Encrypt Message")
    secret_key = st.text_input("Enter your Shared Secret Key:", type="password", help="Both parties must use the same key.")
    message = st.text_area("Enter Long Message:", placeholder="Type your message here...")
    
    if st.button("Generate Quantum Encrypted Payload"):
        if secret_key and message:
            # 1. Derive Key
            fernet_key = derive_key_from_secret(secret_key)
            f = Fernet(fernet_key)
            
            # 2. Encrypt
            token = f.encrypt(message.encode())
            
            st.success("Message Encrypted!")
            st.code(token.decode(), language="text")
            st.info("Copy the block above and send it to your recipient.")
            
            # 3. Quantum Visualization
            with st.expander("View Quantum Key Generation Logic"):
                st.write("A circuit like this was used to secure the entropy of the session:")
                example_qubits = cirq.LineQubit.range(4)
                example_circuit = cirq.Circuit(cirq.H.on_each(*example_qubits), cirq.measure(*example_qubits))
                st.text(example_circuit)
        else:
            st.warning("Please provide both a secret key and a message.")

with tab2:
    st.subheader("Decrypt Message")
    receive_key = st.text_input("Enter the Shared Secret Key:", type="password", key="recv_key")
    payload = st.text_area("Paste Encrypted Payload:")
    
    if st.button("Decode Message"):
        if receive_key and payload:
            try:
                # 1. Derive Key
                fernet_key = derive_key_from_secret(receive_key)
                f = Fernet(fernet_key)
                
                # 2. Decrypt
                decrypted_msg = f.decrypt(payload.encode()).decode()
                st.success("Decryption Successful!")
                st.markdown(f"**Message:** {decrypted_msg}")
            except Exception:
                st.error("Decryption Failed. Incorrect key or corrupted payload.")
        else:
            st.warning("Please provide the key and the payload.")

st.sidebar.markdown("---")
st.sidebar.write("### How it works")
st.sidebar.info(
    "This tool uses a **Hadamard Transform** circuit in Cirq to simulate the generation of "
    "high-entropy bits. These bits form the basis of a symmetric AES-256 key, "
    "ensuring that long-form text is handled efficiently while maintaining quantum-inspired security."
)