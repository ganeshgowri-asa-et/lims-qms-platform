"""
Digital Signature Pad Component
"""
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime


def signature_pad(key="signature"):
    """
    Display a digital signature pad for capturing user signatures.

    Args:
        key: Unique identifier for the signature pad

    Returns:
        dict: Signature data including base64 image, timestamp, and signer info
    """

    st.markdown("### ✍️ Digital Signature")

    # HTML/JS for signature pad using canvas
    signature_html = """
    <div style="border: 2px solid #ccc; border-radius: 5px; padding: 10px; background: white;">
        <canvas id="signaturePad" width="500" height="200" style="border: 1px solid #ddd; cursor: crosshair;"></canvas>
        <br>
        <button onclick="clearSignature()" style="margin-top: 10px; padding: 5px 15px;">Clear</button>
        <button onclick="saveSignature()" style="margin-top: 10px; padding: 5px 15px; background: #1f77b4; color: white; border: none; border-radius: 3px;">Save Signature</button>
    </div>

    <script>
        const canvas = document.getElementById('signaturePad');
        const ctx = canvas.getContext('2d');
        let isDrawing = false;
        let lastX = 0;
        let lastY = 0;

        canvas.addEventListener('mousedown', startDrawing);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', stopDrawing);
        canvas.addEventListener('mouseout', stopDrawing);

        // Touch support for mobile
        canvas.addEventListener('touchstart', handleTouchStart);
        canvas.addEventListener('touchmove', handleTouchMove);
        canvas.addEventListener('touchend', stopDrawing);

        function startDrawing(e) {
            isDrawing = true;
            [lastX, lastY] = [e.offsetX, e.offsetY];
        }

        function draw(e) {
            if (!isDrawing) return;
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 2;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';

            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
            ctx.lineTo(e.offsetX, e.offsetY);
            ctx.stroke();
            [lastX, lastY] = [e.offsetX, e.offsetY];
        }

        function stopDrawing() {
            isDrawing = false;
        }

        function handleTouchStart(e) {
            e.preventDefault();
            const touch = e.touches[0];
            const rect = canvas.getBoundingClientRect();
            lastX = touch.clientX - rect.left;
            lastY = touch.clientY - rect.top;
            isDrawing = true;
        }

        function handleTouchMove(e) {
            if (!isDrawing) return;
            e.preventDefault();
            const touch = e.touches[0];
            const rect = canvas.getBoundingClientRect();
            const x = touch.clientX - rect.left;
            const y = touch.clientY - rect.top;

            ctx.strokeStyle = '#000';
            ctx.lineWidth = 2;
            ctx.lineJoin = 'round';
            ctx.lineCap = 'round';

            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
            ctx.lineTo(x, y);
            ctx.stroke();

            lastX = x;
            lastY = y;
        }

        function clearSignature() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }

        function saveSignature() {
            const dataURL = canvas.toDataURL('image/png');
            window.parent.postMessage({type: 'signature', data: dataURL}, '*');
            alert('Signature saved!');
        }
    </script>
    """

    # Display the signature pad
    components.html(signature_html, height=300)

    # Alternative: Simple file upload for signature
    st.markdown("**Or upload a signature image:**")
    uploaded_sig = st.file_uploader(
        "Upload signature",
        type=['png', 'jpg', 'jpeg'],
        key=f"{key}_upload",
        help="Upload a pre-signed signature image"
    )

    # Signature metadata
    if uploaded_sig or st.session_state.get(f'{key}_signed', False):
        col1, col2 = st.columns(2)

        with col1:
            signer_name = st.text_input(
                "Signer Name*",
                value=st.session_state.get('user', {}).get('full_name', ''),
                key=f"{key}_name"
            )

        with col2:
            signer_designation = st.text_input(
                "Designation*",
                value=st.session_state.get('user', {}).get('role', ''),
                key=f"{key}_designation"
            )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"📅 Signature timestamp: {timestamp}")

        if st.checkbox("I confirm this is my digital signature", key=f"{key}_confirm"):
            return {
                'signed': True,
                'signer': signer_name,
                'designation': signer_designation,
                'timestamp': timestamp,
                'ip_address': 'Captured from request',
                'signature_image': uploaded_sig
            }

    return None


def display_signature(signature_data):
    """
    Display a saved signature with metadata.

    Args:
        signature_data: Dictionary containing signature information
    """
    if not signature_data:
        st.info("No signature available")
        return

    st.markdown("### ✅ Digital Signature")

    with st.container():
        col1, col2 = st.columns([2, 3])

        with col1:
            if signature_data.get('signature_image'):
                st.image(signature_data['signature_image'], caption="Signature", width=200)
            else:
                st.markdown("📝 Signature on file")

        with col2:
            st.markdown(f"**Signed by:** {signature_data.get('signer', 'Unknown')}")
            st.markdown(f"**Designation:** {signature_data.get('designation', 'N/A')}")
            st.markdown(f"**Timestamp:** {signature_data.get('timestamp', 'N/A')}")
            st.markdown(f"**IP Address:** {signature_data.get('ip_address', 'N/A')}")

            if signature_data.get('verified', False):
                st.success("✅ Signature verified")
            else:
                st.warning("⚠️ Signature pending verification")


def multi_signature_workflow(roles=None):
    """
    Multi-level signature workflow for approvals.

    Args:
        roles: List of roles that need to sign (e.g., ['Doer', 'Checker', 'Approver'])
    """
    if not roles:
        roles = ['Doer', 'Checker', 'Approver']

    st.markdown("### 📋 Multi-Level Signature Workflow")

    # Initialize signature state
    if 'signatures' not in st.session_state:
        st.session_state.signatures = {}

    for role in roles:
        with st.expander(f"✍️ {role} Signature", expanded=False):
            if role not in st.session_state.signatures:
                # Signature not yet captured
                signature = signature_pad(key=f"sig_{role}")

                if signature:
                    st.session_state.signatures[role] = signature
                    st.success(f"✅ {role} signature captured")
                    st.rerun()
            else:
                # Signature already captured
                display_signature(st.session_state.signatures[role])

                if st.button(f"🔄 Re-sign as {role}", key=f"resign_{role}"):
                    del st.session_state.signatures[role]
                    st.rerun()

    # Check if all signatures are complete
    all_signed = all(role in st.session_state.signatures for role in roles)

    if all_signed:
        st.success("✅ All required signatures captured!")
        return True
    else:
        pending_roles = [role for role in roles if role not in st.session_state.signatures]
        st.info(f"⏳ Pending signatures from: {', '.join(pending_roles)}")
        return False
